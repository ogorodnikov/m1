from qiskit import QuantumCircuit

from qiskit.circuit.library import Diagonal


def build_phase_oracle(secrets, elements_count):
    
    diagonal_elements = [1] * elements_count
    
    for secret in secrets:
        secret_string = ''.join('1' if letter == '1' else '0' for letter in secret)
        secret_index = int(secret_string, 2)
        diagonal_elements[secret_index] = -1

    phase_oracle = Diagonal(diagonal_elements)
    phase_oracle.name = 'Phase Oracle'
    
    return phase_oracle
    
    
def build_diffuser(qubits_count):
    
    diffuser_circuit = QuantumCircuit(qubits_count)
        
    for qubit in range(qubits_count):
        diffuser_circuit.h(qubit)

    for qubit in range(qubits_count):
        diffuser_circuit.x(qubit)
        
    for qubit in range(1, qubits_count):
        diffuser_circuit.id(qubit)

    diffuser_circuit.h(0)
    diffuser_circuit.mct(list(range(1, qubits_count)), 0)
    diffuser_circuit.h(0)
    
    for qubit in range(1, qubits_count):
        diffuser_circuit.id(qubit)

    for qubit in range(qubits_count):
        diffuser_circuit.x(qubit)

    for qubit in range(qubits_count):
        diffuser_circuit.h(qubit)
        
    diffuser_circuit.name = 'Diffuser'
    
    return diffuser_circuit
    

def grover(run_values, task_log):
    
    secrets = [value for key, value in run_values.items() if 'secret' in key]
    secret_count = len(secrets)
    
    qubits_count = len(max(secrets, key=len))
    qubits = range(qubits_count)

    elements_count = 2 ** qubits_count
    
    repetitions =  (elements_count / secret_count) ** 0.5 * 3.14 / 4
    repetitions_count = int(repetitions)
    
    task_log(f'GROVER secrets: {secrets}')
    task_log(f'GROVER secret_count: {secret_count}')
    task_log(f'GROVER qubits_count: {qubits_count}')
    task_log(f'GROVER elements_count: {elements_count}')
    
    task_log(f'GROVER repetitions: {repetitions}')
    task_log(f'GROVER repetitions_count: {repetitions_count}')
    
    phase_oracle = build_phase_oracle(secrets, elements_count)
    
    diffuser = build_diffuser(qubits_count)

    circuit = QuantumCircuit(qubits_count)
    
    for qubit in qubits:
        circuit.h(qubit)

    for i in range(repetitions_count):
    
        circuit.barrier()
        circuit.append(phase_oracle, qubits)
        circuit.append(diffuser, qubits)
        
    circuit.measure_all()
    
    task_log(f'GROVER phase_oracle: \n{phase_oracle}')
    task_log(f'GROVER phase_oracle 1 decomposition:')
    task_log(f'{phase_oracle.decompose()}')
    task_log(f'GROVER phase_oracle 2 decomposition:')
    task_log(f'{phase_oracle.decompose().decompose()}')
    task_log(f'GROVER phase_oracle 3 decomposition:')
    task_log(f'{phase_oracle.decompose().decompose().decompose()}')

    task_log(f'GROVER diffuser: \n{diffuser}')
    
    task_log(f'GROVER circuit: \n{circuit}')
    
    return circuit

    
