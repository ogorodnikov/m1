from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister

try:
    from qft import create_qft_circuit
except ModuleNotFoundError:
    from core.algorithms.qft import create_qft_circuit

try:
    from counting import build_diffuser
except ModuleNotFoundError:
    from core.algorithms.counting import build_diffuser


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
                                       
    theta_qubits_count = len(theta_register)    
    node_qubits_count = len(node_register)    
    coin_qubits_count = len(coin_register)
    
                                       
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
    

    # Step Diffuser
    
    step_circuit.h(coin_register)
    step_circuit.z(coin_register)
    step_circuit.cz(coin_register[0], coin_register[-1])
    step_circuit.h(coin_register)
    
    step_circuit.x(coin_register)
    
    # TODO: Imported Grover Diffuser

    # grover_diffuser = build_diffuser(qubits_count=coin_qubits_count)
    # grover_diffuser_gate = grover_diffuser.to_gate()
    
    # print(f'WALK grover_diffuser:\n{grover_diffuser}')
    
    # step_circuit.append(grover_diffuser_gate, coin_register)
    

    # Step Shift
    
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
    
    
    # Controlled Step
    
    controlled_step_circuit = step_circuit.control()
    controlled_step_circuit.name = 'CStep'
    

    # Controlled Steps
    
    controlled_steps_circuit = QuantumCircuit(theta_register,
                                              node_register,
                                              coin_register, 
                                              name='CSteps')
    
    for theta_qubit_index, theta_qubit in enumerate(theta_register):
        
        iterations_count = 2 ** theta_qubit_index
        
        for iteration in range(iterations_count):
            
            iteration_qubits = [theta_qubit, *node_register, *coin_register]
            
            controlled_steps_circuit.append(controlled_step_circuit, iteration_qubits)
            
    inverted_controlled_steps_circuit = controlled_steps_circuit.inverse()
    inverted_controlled_steps_circuit.name = 'ICSteps'

    print(f'WALK controlled_steps_circuit:\n{controlled_steps_circuit}')
    print(f'WALK inverted_controlled_steps_circuit:\n{inverted_controlled_steps_circuit}')
  

    # QFT
    
    qft_circuit = create_qft_circuit(theta_qubits_count, inverted=False)
    iqft_circuit = create_qft_circuit(theta_qubits_count, inverted=True)

    print(f'WALK qft_circuit:\n{qft_circuit}')
    print(f'WALK iqft_circuit:\n{iqft_circuit}')
    
    
    # Phase Estimation

    phase_estimation_circuit = QuantumCircuit(theta_register,
                                              node_register,
                                              coin_register, 
                                              theta_flag_register, 
                                              name='Phase Estimation')

    phase_estimation_circuit.h(theta_register)
    
    phase_estimation_circuit.append(controlled_steps_circuit,
                                    [*theta_register,
                                     *node_register,
                                     *coin_register])
    
    phase_estimation_circuit.append(iqft_circuit, theta_register)
    
    phase_estimation_circuit.append(mark_theta_flag_circuit, 
                                    [*theta_register, *theta_flag_register])

    phase_estimation_circuit.append(qft_circuit, theta_register)

    phase_estimation_circuit.append(inverted_controlled_steps_circuit,
                                    [*theta_register,
                                     *node_register,
                                     *coin_register])

    phase_estimation_circuit.h(theta_register)
    
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
    

def walk_reference():
    
    from qiskit.circuit.library import QFT
    
    
    one_step_circuit = QuantumCircuit(6, name=' ONE STEP')
    
    # Coin operator
    one_step_circuit.h([4,5])
    one_step_circuit.z([4,5])
    one_step_circuit.cz(4,5)
    one_step_circuit.h([4,5])
    one_step_circuit.draw()
    
    
    # Shift operator function for 4d-hypercube
    
    def shift_operator(circuit):
        for i in range(0,4):
            circuit.x(4)
            if i%2==0:
                circuit.x(5)
            circuit.ccx(4,5,i)
    
    shift_operator(one_step_circuit)
    
    one_step_gate = one_step_circuit.to_instruction() 
    one_step_circuit.draw()
    
    
    # Make controlled gates
    inv_cont_one_step = one_step_circuit.inverse().control()
    inv_cont_one_step_gate = inv_cont_one_step.to_instruction()
    cont_one_step = one_step_circuit.control()
    cont_one_step_gate = cont_one_step.to_instruction()
    
    
    inv_qft_gate = QFT(4, inverse=True).to_instruction()  
    qft_gate = QFT(4, inverse=False).to_instruction()
    
    QFT(4, inverse=True).decompose().draw("mpl")
    
    
    phase_circuit =  QuantumCircuit(6, name=' phase oracle ')
    # Mark 1011
    phase_circuit.x(2)
    phase_circuit.h(3)
    phase_circuit.mct([0,1,2], 3)
    phase_circuit.h(3)
    phase_circuit.x(2)
    # Mark 1111
    phase_circuit.h(3)
    phase_circuit.mct([0,1,2],3)
    phase_circuit.h(3)
    phase_oracle_gate = phase_circuit.to_instruction()
    # Phase oracle circuit
    phase_oracle_circuit =  QuantumCircuit(11, name=' PHASE ORACLE CIRCUIT ')
    phase_oracle_circuit.append(phase_oracle_gate, [4,5,6,7,8,9])
    phase_circuit.draw()
    
    
    # Mark q_4 if the other qubits are non-zero 
    mark_auxiliary_circuit = QuantumCircuit(5, name=' mark auxiliary ')
    mark_auxiliary_circuit.x([0,1,2,3,4])
    mark_auxiliary_circuit.mct([0,1,2,3], 4)
    mark_auxiliary_circuit.z(4)
    mark_auxiliary_circuit.mct([0,1,2,3], 4)
    mark_auxiliary_circuit.x([0,1,2,3,4])
    
    mark_auxiliary_gate = mark_auxiliary_circuit.to_instruction()
    mark_auxiliary_circuit.draw()
    
    
    # Phase estimation
    phase_estimation_circuit = QuantumCircuit(11, name=' phase estimation ')
    phase_estimation_circuit.h([0,1,2,3])
    for i in range(0,4):
        stop = 2**i
        for j in range(0,stop):
            phase_estimation_circuit.append(cont_one_step, [i,4,5,6,7,8,9])
    
    # Inverse fourier transform
    phase_estimation_circuit.append(inv_qft_gate, [0,1,2,3])
    
    # Mark all angles theta that are not 0 with an auxiliary qubit
    phase_estimation_circuit.append(mark_auxiliary_gate, [0,1,2,3,10])
    
    # Reverse phase estimation
    phase_estimation_circuit.append(qft_gate, [0,1,2,3])   
    
    for i in range(3,-1,-1):
        stop = 2**i
        for j in range(0,stop):
            phase_estimation_circuit.append(inv_cont_one_step, [i,4,5,6,7,8,9])
    phase_estimation_circuit.barrier(range(0,10))
    phase_estimation_circuit.h([0,1,2,3])
    
    # Make phase estimation gate
    phase_estimation_gate = phase_estimation_circuit.to_instruction()
    phase_estimation_circuit.draw()
    
    
    # Implementation of the full quantum walk search algorithm
    theta_q = QuantumRegister(4, 'theta')
    node_q = QuantumRegister(4, 'node')
    coin_q = QuantumRegister(2, 'coin')
    auxiliary_q = QuantumRegister(1, 'auxiliary')
    creg_c2 = ClassicalRegister(4, 'c')
    circuit = QuantumCircuit(theta_q, node_q, coin_q, auxiliary_q, creg_c2)
    # Apply Hadamard gates to the qubits that represent the nodes and the coin
    circuit.h([4,5,6,7,8,9])
    iterations = 2
    
    for i in range(0,iterations):
        circuit.append(phase_oracle_gate, [4,5,6,7,8,9])
        circuit.append(phase_estimation_gate, [0,1,2,3,4,5,6,7,8,9,10])
    
    circuit.measure(node_q[0], creg_c2[0])
    circuit.measure(node_q[1], creg_c2[1])
    circuit.measure(node_q[2], creg_c2[2])
    circuit.measure(node_q[3], creg_c2[3])
    circuit.draw()
    
    
    return circuit