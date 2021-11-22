from qiskit import QuantumCircuit


def add_bell_pair(circuit, qubit_a, qubit_b):
    
    circuit.h(qubit_a)
    circuit.cx(qubit_a, qubit_b)
    

def add_alice_gates(circuit, qubit_a, qubit_b):
    
    circuit.cx(qubit_a, qubit_b)
    circuit.h(qubit_a)
    
    
def teleport(run_values, task_log):
    
    state = 0 + 1j
    
    alice_source_qubit = 0
    alice_entangled_qubit = 1
    bob_entangled_qubit = 2
    
    quantum_register = QuantumRegister(3, name="q")
    
    classical_register_z = ClassicalRegister(1, name="Classical register Z")
    classical_register_x = ClassicalRegister(1, name="Classical register X")
    
    circuit = QuantumCircuit(quantum_register,
                             classical_register_z,
                             classical_register_x)
    
    circuit.initialize(state, alice_source_qubit)
    
    circuit.barrier()
    
    add_bell_pair(circuit, alice_entangled_qubit, bob_entangled_qubit)
    
    circuit.barrier()    

    add_alice_gates(circuit, alice_source_qubit, alice_entangled_qubit) 
    
    circuit.barrier()
    
    
    
    
    task_log(f'TELEPORT circuit: \n{circuit}')
    
    return circuit