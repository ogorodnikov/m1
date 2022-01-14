from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister

try:
    from qft import create_qft_circuit
except ModuleNotFoundError:
    from core.algorithms.qft import create_qft_circuit

try:
    from grover import build_diffuser
except ModuleNotFoundError:
    from core.algorithms.grover import build_diffuser


def build_phase_oracle(qubits):
    
    qubits_count = len(qubits)
    
    circuit = QuantumCircuit(qubits_count, name="Phase Oracle")
    
    # Example nodes
    
    # Node 1011
    
    circuit.x(2)
    circuit.h(3)
    circuit.mct([0,1,2], 3)
    circuit.h(3)
    circuit.x(2)
    
    # Node 1111
    
    circuit.h(3)
    circuit.mct([0,1,2],3)
    circuit.h(3)
    
    return circuit
    

def build_phase_estimation_circuit(theta_register, node_register,
                                   coin_register, theta_flag_register):
                                       
    # Mark Theta Flag

    theta_qubits = theta_register
    theta_flag_qubit = theta_flag_register
    mark_theta_qubits = [*theta_register, *theta_flag_register]
                               
    mark_theta_flag_circuit = QuantumCircuit(theta_register, theta_flag_register,
                                             name="Mark Theta Flag")
    
    mark_theta_flag_circuit.x(mark_theta_qubits)
    mark_theta_flag_circuit.mct(theta_qubits, theta_flag_qubit)
    mark_theta_flag_circuit.z(theta_flag_qubit)
    mark_theta_flag_circuit.mct(theta_qubits, theta_flag_qubit)
    mark_theta_flag_circuit.x(mark_theta_qubits)

    print(f'WALK mark_theta_flag_circuit:\n{mark_theta_flag_circuit}')
    
    
    # Step
    
    step_circuit = QuantumCircuit(node_register, coin_register, name='Step')
    
    coin_qubits_count = len(coin_register)
    
    grover_diffuser = build_diffuser(qubits_count=coin_qubits_count)
    
    print(f'WALK grover_diffuser:\n{grover_diffuser}')
    
    # step_circuit.h(coin_register)
    # step_circuit.z(coin_register)
    # step_circuit.cz(coin_register[0], coin_register[-1])
    # step_circuit.h(coin_register)
    
    step_circuit.append(grover_diffuser, coin_register)
    

    # Shift
    
    node_qubits_count = len(node_register)
    
    previous_node_bits = '0' * coin_qubits_count
    
    for node in range(node_qubits_count):

        node_bits = bin(int(node))[2:]
        node_bits_filled = node_bits.zfill(coin_qubits_count)
        node_bits_reversed = ''.join(reversed(node_bits_filled))
        
        node_differences = ''.join('1' if node_bit != previous_node_bit else '0'
                                   for node_bit, previous_node_bit
                                   in zip(node_bits_reversed, previous_node_bits))
        
        previous_node_bits = node_bits_reversed
        
        for coin_qubit_index, node_difference in enumerate(node_differences):
            
            if node_difference == '1':
                
                coin_qubit = coin_register[coin_qubit_index]
                
                step_circuit.x(coin_qubit)
        
        step_circuit.ccx(*coin_register, node)
    
        print(f'WALK node_bits: {node_bits}')
        print(f'WALK node_bits_filled: {node_bits_filled}')
        print(f'WALK node_bits_reversed: {node_bits_reversed}')
        
        print(f'WALK node_differences: {node_differences}')
        print(f'WALK previous_node_bits: {previous_node_bits}')
    
    print(f'WALK step_circuit:\n{step_circuit}')
    
    
    # Phase Estimation

    phase_estimation_circuit = QuantumCircuit(theta_register,
                                              node_register,
                                              coin_register, 
                                              theta_flag_register, 
                                              name='Phase Estimation')
    
    phase_estimation_circuit.append(mark_theta_flag_circuit, 
                                    [*theta_register, *theta_flag_register])



    return phase_estimation_circuit
    

def walk(run_values, task_log):
    
    ''' https://qiskit.org/textbook/ch-algorithms/quantum-walk-search-algorithm.html '''
    
    # Inputs
    
    iterations_count = 2
    
    # Registers
    
    theta_register = QuantumRegister(4, 'theta')
    node_register = QuantumRegister(4, 'node')
    coin_register = QuantumRegister(2, 'coin')
    theta_flag_register = QuantumRegister(1, 'theta_flag')
    
    measure_register = ClassicalRegister(4, 'measure')
    
    
    # Circuit
    
    circuit = QuantumCircuit(theta_register,
                             node_register,
                             coin_register,
                             theta_flag_register,
                             measure_register)
                             
    phase_oracle_qubits = [*node_register, *coin_register]
    
    phase_estimation_qubits = [*theta_register, 
                               *node_register,
                               *coin_register,
                               *theta_flag_register]
    
    circuit.h(phase_oracle_qubits)
    
    phase_oracle = build_phase_oracle(phase_oracle_qubits)
    phase_estimation = build_phase_estimation_circuit(theta_register, 
                                                      node_register,
                                                      coin_register,
                                                      theta_flag_register)

    for iteration in range(iterations_count):
        
        circuit.append(phase_oracle, phase_oracle_qubits)
        circuit.append(phase_estimation, phase_estimation_qubits)
        
    # Measure
    
    circuit.measure(node_register, measure_register)
    
    # Logs
    
    task_log(f'WALK run_values: {run_values}')
    
    task_log(f'WALK phase_oracle_qubits: {phase_oracle_qubits}')
    task_log(f'WALK phase_oracle:\n{phase_oracle}')
    
    task_log(f'WALK phase_estimation_qubits: {phase_estimation_qubits}')
    task_log(f'WALK phase_estimation:\n{phase_estimation}')
    
    task_log(f'WALK circuit:\n{circuit}')
    
    return circuit