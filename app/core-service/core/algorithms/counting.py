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
    
    
def build_unitary_phase_oracle(secrets, elements_count):
    
    # phase_oracle_circuit = QuantumCircuit(qubits_count)
    
    for secret in secrets:
        
        # diffuser_circuit.mct(list(range(1, qubits_count)), 0)
        
        
        secret_string = ''.join('1' if letter == '1' else '0' for letter in secret)
        secret_index = int(secret_string, 2)
        diagonal_elements[secret_index] = -1

    phase_oracle = Diagonal(diagonal_elements)
    phase_oracle.name = 'Phase Oracle'
    
    return phase_oracle
    

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
    print(f'COUNT phase_oracle:\n{phase_oracle.decompose()}')
    print(f'COUNT phase_oracle:\n{phase_oracle.decompose().decompose().decompose()}')
    
    quit()
    
    return grover_iteration_circuit
    

def quantum_counting(run_values, task_log):
    
    secrets = [value for key, value in run_values.items() if 'secret' in key]
    secret_count = len(secrets)
    
    qubits_count = len(max(secrets, key=len))
    
    grover_iteration_circuit = build_grover_iteration(qubits_count, secrets)
    # grover_iteration_gate = grover_iteration_circuit.to_gate()
    controlled_grover_iteration = grover_iteration_circuit.control()
    
    task_log(f'COUNT run_values: {run_values}')
    task_log(f'COUNT grover_iteration_circuit: {grover_iteration_circuit}')
    # task_log(f'COUNT grover_iteration_gate: {grover_iteration_gate}')
    task_log(f'COUNT controlled_grover_iteration: {controlled_grover_iteration}')