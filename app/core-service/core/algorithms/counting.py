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
    
    
def build_unitary_phase_oracle(secrets, qubits_count):
    
    phase_oracle_circuit = QuantumCircuit(qubits_count + 1)
    
    ancilla_qubit = qubits_count
    
    phase_oracle_circuit.x(ancilla_qubit)
    phase_oracle_circuit.h(ancilla_qubit)
    
    for secret in secrets:
        
        control_qubits = [qubit_index for qubit_index, secret_digit in enumerate(secret) 
                          if secret_digit == '1']
        
        phase_oracle_circuit.mct(control_qubits, ancilla_qubit)
        
    phase_oracle_circuit.h(ancilla_qubit)
    phase_oracle_circuit.x(ancilla_qubit)
        
    phase_oracle_circuit.name = 'Unitary Phase Oracle'
    
    print(f'COUNT secrets: {secrets}')
    print(f'COUNT phase_oracle_circuit:\n{phase_oracle_circuit}')
    
    return phase_oracle_circuit
    

def build_grover_iteration(qubits_count, secrets):
    
    qubits = range(qubits_count)
    ancilla_qubit = qubits_count
    
    grover_iteration_circuit = QuantumCircuit(qubits_count + 1)
    
    phase_oracle = build_unitary_phase_oracle(secrets=secrets, qubits_count=qubits_count)
    diffuser = build_diffuser(qubits_count=qubits_count)
    
    phase_oracle_gate = phase_oracle.to_gate()
    diffuser_gate = diffuser.to_gate()
    
    grover_iteration_circuit.append(phase_oracle_gate, [*qubits, ancilla_qubit])
    grover_iteration_circuit.append(diffuser_gate, qubits)

    print(f'COUNT [*qubits, ancilla_qubit]: {[*qubits, ancilla_qubit]}')
    print(f'COUNT grover_iteration_circuit:\n{grover_iteration_circuit}')
    print(f'COUNT phase_oracle:\n{phase_oracle}')
    
    return grover_iteration_circuit
    

def quantum_counting(run_values, task_log):
    
    secrets = [value for key, value in run_values.items() if 'secret' in key]
    secret_count = len(secrets)
    
    qubits_count = len(max(secrets, key=len))
    
    grover_iteration_circuit = build_grover_iteration(qubits_count, secrets)
    
    grover_iteration_gate = grover_iteration_circuit.to_gate()
    # controlled_grover_iteration = grover_iteration_circuit.control()
    
    task_log(f'COUNT run_values: {run_values}')
    task_log(f'COUNT grover_iteration_circuit:\n{grover_iteration_circuit}')
    
    task_log(f'COUNT grover_iteration_gate: {grover_iteration_gate}')
    # task_log(f'COUNT controlled_grover_iteration: {controlled_grover_iteration}')