from qiskit import QuantumCircuit


def teleport(run_values, task_log):
    
    
    
    # state = 0, 1
    state = −0.38591 − 0.11057j, −0.31966 + 0.85829j
    
    alice_source_qubit = 0
    alice_entangled_qubit = 1
    bob_entangled_qubit = 2
    
    bit_x = 0
    bit_z = 1
    
    quantum_register = QuantumRegister(3, name="q")
    
    classical_register_z = ClassicalRegister(1, name="Classical register Z")
    classical_register_x = ClassicalRegister(1, name="Classical register X")
    
    circuit = QuantumCircuit(quantum_register,
                             classical_register_z,
                             classical_register_x)
    
    circuit.initialize(state, alice_source_qubit)
    
    circuit.barrier()
    
    # add Bell pair
    
    circuit.h(alice_source_qubit)
    circuit.cx(alice_source_qubit, alice_entangled_qubit)
    
    circuit.barrier()
    
    # add Alice gates

    circuit.cx(alice_source_qubit, alice_entangled_qubit)
    circuit.h(alice_source_qubit)
    
    circuit.barrier()
    
    # measure
    
    circuit.measure(alice_entangled_qubit, bit_x)
    circuit.measure(alice_source_qubit, bit_z)
    
    # add Bob gates
    
    circuit.x(bob_entangled_qubit).c_if(bit_x, 1)
    circuit.z(bob_entangled_qubit).c_if(bit_z, 1)
    
    
    task_log(f'TELEPORT run_values: {run_values}')
    
    task_log(f'TELEPORT state: {state}')
    
    task_log(f'TELEPORT alice_source_qubit: {alice_source_qubit}')
    task_log(f'TELEPORT alice_entangled_qubit: {alice_entangled_qubit}')
    task_log(f'TELEPORT bob_entangled_qubit: {bob_entangled_qubit}')
    
    task_log(f'TELEPORT bit_x: {bit_x}')
    task_log(f'TELEPORT bit_z: {bit_z}')
    
    task_log(f'TELEPORT circuit: \n{circuit}')
    
    return circuit