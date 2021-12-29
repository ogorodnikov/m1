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
    
    
    # CGRIT
    
    grover_iteration_circuit = example_grover_iteration(qubits_count, secrets)
    
    grover_iteration_gate = grover_iteration_circuit.to_gate()
    controlled_grover_iteration = grover_iteration_gate.control()
    
    grover_iteration_gate.label = "Grover Iteration Gate"
    
    
    # IQFT
    
    iqft_circuit = create_qft_circuit(4, inverted=True)
    
    example_qft_circuit = example_qft(4)
    example_iqft_gate = example_qft_circuit.to_gate().inverse()
    
    
    # Circuit
    
    counting_qubits_count = 4
    searching_qubits_count = 4
    total_qubits_count = counting_qubits_count + searching_qubits_count
    
    counting_qubits = list(range(counting_qubits_count))
    searching_qubits = list(range(counting_qubits_count, total_qubits_count))
    all_qubits = list(range(total_qubits_count))
    
    measurement_bits_count = counting_qubits_count
    
    circuit = QuantumCircuit(total_qubits_count, measurement_bits_count)
    
    circuit.h(all_qubits)
    
    
    # Apply CGRITs
    
    for counting_qubit in counting_qubits:
        
        iterations_count = 2 ** counting_qubit
        
        for iteration in range(iterations_count):
            
            task_log(f'COUNT iteration: {iteration}')  
        
    
    task_log(f'COUNT run_values: {run_values}')
    
    task_log(f'COUNT grover_iteration_circuit:\n{grover_iteration_circuit}')
    task_log(f'COUNT grover_iteration_gate:\n{grover_iteration_gate}')
    task_log(f'COUNT controlled_grover_iteration:\n{controlled_grover_iteration}')
    
    task_log(f'COUNT iqft_circuit:\n{iqft_circuit}')
    
    task_log(f'COUNT example_qft_circuit:\n{example_qft_circuit}')
    task_log(f'COUNT example_iqft_gate:\n{example_iqft_gate}')
    
    task_log(f'COUNT circuit:\n{circuit}')
    
    task_log(f'COUNT counting_qubits:\n{counting_qubits}')
    task_log(f'COUNT searching_qubits:\n{searching_qubits}')
    task_log(f'COUNT all_qubits:\n{all_qubits}')
    