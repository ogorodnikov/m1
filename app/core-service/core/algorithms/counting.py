from qiskit import QuantumCircuit

try:
    from grover import build_phase_oracle
    from grover import build_diffuser
except ModuleNotFoundError:
    from core.algorithms.grover import build_phase_oracle
    from core.algorithms.grover import build_diffuser

try:
    from qft import create_qft_circuit
except ModuleNotFoundError:
    from core.algorithms.qft import create_qft_circuit
    
import numpy as np
    
    
def example_grover_iteration(qubits_count, secrets):

    circuit = QuantumCircuit(4)
    
    # Oracle
    circuit.h([2,3])
    circuit.ccx(0,1,2)
    circuit.h(2)
    circuit.x(2)
    circuit.ccx(0,2,3)
    circuit.x(2)
    circuit.h(3)
    circuit.x([1,3])
    circuit.h(2)
    circuit.mct([0,1,3],2)
    circuit.x([1,3])
    circuit.h(2)
    
    # circuit.barrier()
    
    # Diffuser
    circuit.h(range(3))
    circuit.x(range(3))
    circuit.z(3)
    circuit.mct([0,1,2],3)
    circuit.x(range(3))
    circuit.h(range(3))
    circuit.z(3)
    
    return circuit
    
    
def example_qft(n):
    
    circuit = QuantumCircuit(4)
    
    def swap_registers(circuit, n):
        for qubit in range(n//2):
            circuit.swap(qubit, n-qubit-1)
        return circuit
        
    def qft_rotations(circuit, n):
        
        if n == 0:
            return circuit
            
        n -= 1
        circuit.h(n)
        
        for qubit in range(n):
            circuit.cp(np.pi/2**(n-qubit), qubit, n)
            
        qft_rotations(circuit, n)
    
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    
    return circuit

def quantum_counting(run_values, task_log):
    
    secrets = [value for key, value in run_values.items() if 'secret' in key]
    secret_count = len(secrets)
    
    qubits_count = len(max(secrets, key=len))
    
    grover_iteration_circuit = example_grover_iteration(qubits_count, secrets)
    
    grover_iteration_gate = grover_iteration_circuit.to_gate()
    controlled_grover_iteration = grover_iteration_gate.control()
    
    grover_iteration_gate.label = "Grover Iteration Gate"
    
    iqft_circuit = create_qft_circuit(4, inverted=True)
    example_qft_circuit = example_qft(4)
    
    task_log(f'COUNT run_values: {run_values}')
    
    task_log(f'COUNT grover_iteration_circuit:\n{grover_iteration_circuit}')
    task_log(f'COUNT grover_iteration_gate:\n{grover_iteration_gate}')
    task_log(f'COUNT controlled_grover_iteration:\n{controlled_grover_iteration}')
    
    task_log(f'COUNT iqft_circuit:\n{iqft_circuit}')
    task_log(f'COUNT example_qft_circuit:\n{example_qft_circuit}')
    