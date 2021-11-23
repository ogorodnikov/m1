from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister

from qiskit.quantum_info import random_statevector


def teleport(run_values, task_log):
    
    alpha = run_values.get('alpha')
    beta = run_values.get('beta')
    
    if 'random' in (alpha, beta):
        state = random_statevector(dims=2)
        
    else:
        state = complex(alpha), complex(beta)
    
    alice_source_qubit = 0
    alice_entangled_qubit = 1
    bob_entangled_qubit = 2
    
    quantum_register = QuantumRegister(3, name="q")
    
    bit_x = 0
    bit_z = 1
    
    classical_register_z = ClassicalRegister(1, name="bit_z")
    classical_register_x = ClassicalRegister(1, name="bit_x")
    
    circuit = QuantumCircuit(quantum_register,
                             classical_register_z,
                             classical_register_x)
    
    circuit.initialize(state, alice_source_qubit)
    
    circuit.barrier()
    
    # add Bell pair
    
    circuit.h(alice_entangled_qubit)
    circuit.cx(alice_entangled_qubit, bob_entangled_qubit)
    
    circuit.barrier()
    
    # add Alice gates

    circuit.cx(alice_source_qubit, alice_entangled_qubit)
    circuit.h(alice_source_qubit)
    
    circuit.barrier()
    
    # add Bob gates
    
    circuit.cx(alice_entangled_qubit, bob_entangled_qubit)
    circuit.cz(alice_source_qubit, bob_entangled_qubit)

    circuit.barrier()
    
    # Measure
    
    circuit.measure(alice_entangled_qubit, bit_x)
    circuit.measure(alice_source_qubit, bit_z)
    
    
    task_log(f'TELEPORT run_values: {run_values}')
    
    task_log(f'TELEPORT alpha: {alpha}')
    task_log(f'TELEPORT beta: {beta}')
    task_log(f'TELEPORT state: {state}')
    
    task_log(f'TELEPORT alice_source_qubit: {alice_source_qubit}')
    task_log(f'TELEPORT alice_entangled_qubit: {alice_entangled_qubit}')
    task_log(f'TELEPORT bob_entangled_qubit: {bob_entangled_qubit}')
    
    task_log(f'TELEPORT bit_x: {bit_x}')
    task_log(f'TELEPORT bit_z: {bit_z}')
    
    task_log(f'TELEPORT circuit: \n{circuit}')
    
    return circuit