from itertools import combinations

from qiskit import Aer, ClassicalRegister, QuantumRegister, QuantumCircuit, execute
from qiskit.tools.monitor import job_monitor

from qiskit.circuit.library import Diagonal


def build_dj_oracle(secret):
    
    return
    
    diagonal_elements = [1] * elements_count
    
    for secret in secrets:
        secret_string = ''.join('1' if letter == '1' else '0' for letter in secret)
        secret_index = int(secret_string, 2)
        diagonal_elements[secret_index] = -1

    phase_oracle = Diagonal(diagonal_elements)
    phase_oracle.name = 'Phase Oracle'
    
    return phase_oracle
    
    
def dj(run_values, task_log):
    
    secret = run_values.get('secret')
    
    limited_secret_len = 2 ** int(len(secret) ** 0.5)
    
    limited_secret = secret[:limited_secret_len]
    
    qubit_count = len(limited_secret)
    
    dj_oracle = build_dj_oracle(limited_secret)

    circuit = QuantumCircuit(qubit_count)

    task_log(f'DJ secret: {secret}')
    task_log(f'DJ limited_secret: {limited_secret}')
    task_log(f'DJ qubit_count: {qubit_count}')

    task_log(f'SUDOKU dj_oracle: \n{dj_oracle}')
    task_log(f'SUDOKU circuit: \n{circuit}')

    # return circuit