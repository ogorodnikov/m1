from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister


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
    
    # mark_theta_flag_gate = mark_theta_flag_circuit.to_instruction()
    
    # print(f'WALK mark_theta_flag_circuit:\n{mark_theta_flag_circuit}')
        
    # circuit = QuantumCircuit(11, name="Phase Estimation")
    
    # circuit.append(mark_theta_flag_gate, [0, 1, 2, 3, 10])
    
    # print(f'WALK phase_estimation_circuit:\n{circuit}')
    
    
    # mark_theta_flag_circuit = QuantumCircuit(5, 
    #                                          name="Mark Theta Flag")
                                             
    # mark_theta_flag_circuit.x([0,1,2,3,4])
    # mark_theta_flag_circuit.mct([0,1,2,3], 4)
    # mark_theta_flag_circuit.z(4)
    # mark_theta_flag_circuit.mct([0,1,2,3], 4)
    # mark_theta_flag_circuit.x([0,1,2,3,4])
    
    print(f'WALK mark_theta_flag_circuit:\n{mark_theta_flag_circuit}')
    
    # Phase estimation
    
    
    circuit = QuantumCircuit(theta_register, node_register,
                                   coin_register, theta_flag_register, name=' phase estimation ')
                                   
    
    circuit.append(mark_theta_flag_circuit, [*theta_register, 
                                             *theta_flag_register])
    
    
    print(f'WALK phase_estimation_circuit:\n{circuit}')
    

    # quit()
    
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