from qiskit import *
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import backend_overview, job_monitor

from qiskit.circuit.library import Diagonal

# from qiskit_textbook.problems import grover_problem_oracle

import math
import numpy as np

def grover(run_values):
    
    run_values = {'secret': ('1010',),}
    
    secrets = run_values.get('secret')
    secret_count = len(secrets)
    
    qubit_count = len(max(secrets, key=len))
    elements_count = 2 ** qubit_count
    
    diagonal_elements = [1] * elements_count
    
    for secret in secrets:
        secret_string = ''.join('1' if letter == '1' else '0' for letter in secret)
        secret_index = int(secret_string, 2)
        diagonal_elements[secret_index] = -1

    phase_oracle = Diagonal(diagonal_elements)
    phase_oracle.name = 'Phase Oracle'   
    
    repetitions =  (elements_count / secret_count) ** 0.5 * 3.14 / 4
    repetitions_count = int(repetitions)
    
    iterations_count = math.floor(np.pi * np.sqrt(2 ** qubit_count / secret_count) / 4)

    print(f'GROVER secrets: {secrets}')
    print(f'GROVER secret_count: {secret_count}')
    print(f'GROVER qubit_count: {qubit_count}')
    print(f'GROVER elements_count: {elements_count}')
    
    print(f'GROVER repetitions: {repetitions}')
    print(f'GROVER repetitions_count: {repetitions_count}')
    print(f'GROVER iterations_count: {iterations_count}')
    print(f'GROVER diagonal_elements: {diagonal_elements}')
    
    # quit()
    
    # oracle = grover_problem_oracle(qubit_count, variant=10, print_solutions=True)
    
    print(phase_oracle.decompose())
    print(phase_oracle.decompose().decompose())
    print(phase_oracle.decompose().decompose().decompose())
    
    # quit()


    for repetitions_count in range(1, 4):
        
        print(f'GROVER repetitions_count: {repetitions_count}')
        
        circuit = QuantumCircuit(qubit_count)
        
        for qubit in range(qubit_count):
            circuit.h(qubit)
        
        circuit.append(phase_oracle, range(qubit_count))
    
        for i in range(repetitions_count):
        
            circuit.barrier()
            
            for qubit in range(qubit_count):
                circuit.h(qubit)
        
            for qubit in range(qubit_count):
                circuit.x(qubit)
                
            for qubit in range(1, qubit_count):
                circuit.i(qubit)
        
            circuit.h(0)
            circuit.mct(list(range(1, qubit_count)), 0)
            circuit.h(0)
            
            for qubit in range(1, qubit_count):
                circuit.i(qubit)
        
            for qubit in range(qubit_count):
                circuit.x(qubit)
        
            for qubit in range(qubit_count):
                circuit.h(qubit)
            
    
        circuit.measure_all()
        
        print(circuit.draw(output='text', fold=200))
    
    
        # run
        
        backend = Aer.get_backend('qasm_simulator')
        
        job = execute(circuit, backend=backend, shots=1000)
        
        result = job.result()
        
        counts = result.get_counts()
        
        [print(f'{state}: {count}') for state, count in sorted(counts.items())]

    return counts
    
result = grover('bonya')

