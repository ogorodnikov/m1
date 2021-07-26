from qiskit import *

from qiskit.circuit.library import Diagonal

from core import app


def build_phase_oracle(secrets, elements_count):
    
    diagonal_elements = [1] * elements_count
    
    for secret in secrets:
        secret_string = ''.join('1' if letter == '1' else '0' for letter in secret)
        secret_index = int(secret_string, 2)
        diagonal_elements[secret_index] = -1

    phase_oracle = Diagonal(diagonal_elements)
    phase_oracle.name = 'Phase Oracle'
    
    return phase_oracle
    
    
def build_diffuser(qubit_count):
    
    diffuser_circuit = QuantumCircuit(qubit_count)
        
    for qubit in range(qubit_count):
        diffuser_circuit.h(qubit)

    for qubit in range(qubit_count):
        diffuser_circuit.x(qubit)
        
    for qubit in range(1, qubit_count):
        diffuser_circuit.i(qubit)

    diffuser_circuit.h(0)
    diffuser_circuit.mct(list(range(1, qubit_count)), 0)
    diffuser_circuit.h(0)
    
    for qubit in range(1, qubit_count):
        diffuser_circuit.i(qubit)

    for qubit in range(qubit_count):
        diffuser_circuit.x(qubit)

    for qubit in range(qubit_count):
        diffuser_circuit.h(qubit)
        
    diffuser_circuit.name = 'Diffuser'
    
    return diffuser_circuit
    

def grover(run_values):
    
    secrets = [value for key, value in run_values.items() if 'secret' in key]
    secret_count = len(secrets)
    
    qubit_count = len(max(secrets, key=len))
    qubits = range(qubit_count)

    elements_count = 2 ** qubit_count
    
    repetitions =  (elements_count / secret_count) ** 0.5 * 3.14 / 4
    repetitions_count = int(repetitions)
    
    app.logger.info(f'GROVER secrets: {secrets}')
    app.logger.info(f'GROVER secret_count: {secret_count}')
    app.logger.info(f'GROVER qubit_count: {qubit_count}')
    app.logger.info(f'GROVER elements_count: {elements_count}')
    
    app.logger.info(f'GROVER repetitions: {repetitions}')
    app.logger.info(f'GROVER repetitions_count: {repetitions_count}')
    
    phase_oracle = build_phase_oracle(secrets, elements_count)
    
    diffuser = build_diffuser(qubit_count)

    circuit = QuantumCircuit(qubit_count)
    
    for qubit in qubits:
        circuit.h(qubit)

    for i in range(repetitions_count):
    
        circuit.barrier()
        circuit.append(phase_oracle, qubits)
        circuit.append(diffuser, qubits)
        
    circuit.measure_all()
    
    app.logger.info(f'GROVER phase_oracle: \n{phase_oracle}')
    app.logger.info(f'GROVER phase_oracle 1 decomposition:')
    app.logger.info(phase_oracle.decompose())
    app.logger.info(f'GROVER phase_oracle 2 decomposition:')
    app.logger.info(phase_oracle.decompose().decompose())
    app.logger.info(f'GROVER phase_oracle 3 decomposition:')
    app.logger.info(phase_oracle.decompose().decompose().decompose())

    app.logger.info(f'GROVER diffuser: \n{diffuser}')
    
    app.logger.info(f'GROVER circuit: \n{circuit}')
    
    return circuit

    
