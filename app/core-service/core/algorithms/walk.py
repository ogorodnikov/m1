from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister


def walk(run_values, task_log):
    
    
    # Inputs
    
    iterations_count = 2
    
    # Registers
    
    theta_register = QuantumRegister(4, 'theta')
    node_register = QuantumRegister(4, 'node')
    coin_register = QuantumRegister(2, 'coin')
    auxilary_register = QuantumRegister(1, 'auxilary')
    
    measure_register = ClassicalRegister(4, 'measure')
    
    
    # Circuit
    
    circuit = QuantumCircuit(theta_register,
                             node_register,
                             coin_register,
                             auxilary_register,
                             measure_register)
                             
    phase_oracle_qubits = [*node_register, *coin_register]
    
    phase_estimation_qubits = [*theta_register, 
                               *node_register,
                               *coin_register,
                               *auxilary_register]
    
    circuit.h(phase_oracle_qubits)
    
    phase_oracle_gate = QuantumCircuit(6)
    phase_estimation_gate = QuantumCircuit(11)
    
    for iteration in range(iterations_count):
        
        circuit.append(phase_oracle_gate, phase_oracle_qubits)
        circuit.append(phase_estimation_gate, phase_estimation_qubits)
        
    
    # Logs
    
    task_log(f'WALK run_values: {run_values}')
    
    # task_log(f'WALK phase_oracle_qubits: {phase_oracle_qubits}')
    # task_log(f'WALK phase_estimation_qubits: {phase_estimation_qubits}')