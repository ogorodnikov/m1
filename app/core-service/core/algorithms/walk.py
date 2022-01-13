from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister

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
    
    # Step
    
    step_circuit = QuantumCircuit(node_register, coin_register, name='Step')
    
    step_qubits_count = len(coin_register)
    
    grover_diffuser = build_diffuser(qubits_count=step_qubits_count)
    
    step_circuit.append(grover_diffuser, coin_register)
    
    print(f'WALK grover_diffuser:\n{grover_diffuser}')    
    print(f'WALK step_circuit:\n{step_circuit}')    
    
    # quit()
    
    # Phase Estimation

    circuit = QuantumCircuit(theta_register,
                             node_register,
                             coin_register, 
                             theta_flag_register, 
                             name='Phase Estimation')
    
    circuit.append(mark_theta_flag_circuit, [*theta_register, 
                                             *theta_flag_register])

    # print(f'WALK mark_theta_flag_circuit:\n{mark_theta_flag_circuit}')

    return circuit
    

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