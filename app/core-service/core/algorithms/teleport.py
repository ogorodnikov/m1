from qiskit import QuantumCircuit


def teleport(run_values, task_log):
    
    state = 0 + 1j
    
    quantum_register = QuantumRegister(3, name="q")
    
    classical_register_z = ClassicalRegister(1, name="Classical register Z")
    classical_register_x = ClassicalRegister(1, name="Classical register X")
    
    circuit = QuantumCircuit(quantum_register,
                             classical_register_z,
                             classical_register_x)
    
    circuit.initialize(state, quantum_register[0])
    
    task_log(f'TELEPORT circuit: \n{circuit}')
    
    return circuit