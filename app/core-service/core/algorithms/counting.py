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
    

def build_grover_iteration(qubits_count, secrets):
    
    qubits = range(qubits_count)
    
    elements_count = 2 ** qubits_count
    
    grover_iteration_circuit = QuantumCircuit(qubits_count)
    
    phase_oracle = build_phase_oracle(secrets=secrets, 
                                      elements_count=elements_count)
                                      
    diffuser = build_diffuser(qubits_count=qubits_count)
    
    grover_iteration_circuit.append(phase_oracle, qubits)
    grover_iteration_circuit.append(diffuser, qubits)

    print(f'COUNT grover_iteration_circuit:\n{grover_iteration_circuit}')
    

def quantum_counting(run_values, task_log):
    
    secrets = [value for key, value in run_values.items() if 'secret' in key]
    secret_count = len(secrets)
    
    qubits_count = len(max(secrets, key=len))
    
    build_grover_iteration(qubits_count, secrets)
    
    task_log(f'COUNT run_values: {run_values}')