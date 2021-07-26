from qiskit import *
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import backend_overview, job_monitor

from qiskit.circuit.library import Diagonal

# from qiskit_textbook.problems import grover_problem_oracle

import math
import numpy as np

def grover(run_values):
    
    run_values = {'secret':'000',}
    
    secret = run_values.get('secret')
    secret_string = ''.join('1' if symbol == '1' else '0' for symbol in secret)
    secret_index = int(secret, 2)
    
    qubit_count = 3
    solutions = (0, 1), #(2, 3)
    
    elements_count = 2 ** qubit_count
    solutions_count = len(solutions)
    
    repetitions =  (elements_count / solutions_count) ** 0.5 * 3.14 / 4
    repetitions_count = int(repetitions)
    
    iterations_count = math.floor(np.pi * np.sqrt(2 ** qubit_count / solutions_count) / 4)
    
    diagonal_elements = [1] * elements_count
    diagonal_elements[secret_index] = -1
    
    phase_oracle = Diagonal(diagonal_elements)
    phase_oracle.name = 'Phase Oracle'    
    
    print(f'GROVER elements_count: {elements_count}')
    print(f'GROVER solutions_count: {solutions_count}')
    print(f'GROVER repetitions: {repetitions}')
    print(f'GROVER repetitions_count: {repetitions_count}')
    print(f'GROVER iterations_count: {iterations_count}')
    print(f'GROVER diagonal_elements: {diagonal_elements}')
    

    
    # oracle = grover_problem_oracle(qubit_count, variant=10, print_solutions=True)
    
    # print(phase_oracle.decompose())
    # print(phase_oracle.decompose().decompose())
    # print(phase_oracle.decompose().decompose().decompose())
    
    quit()


    for repetitions_count in range(1, 4):
        
        print(f'GROVER repetitions_count: {repetitions_count}')
        
        circuit = QuantumCircuit(qubit_count)
        
        circuit.append(phase_oracle, [0, 1, 2])
    
        # for qubit in range(qubit_count):
        #     circuit.h(qubit)
        
        # for pattern in patterns:
        #     circuit.cz(*pattern)
    
        for i in range(repetitions_count):
        
            circuit.barrier()
            
            for qubit in range(qubit_count):
                circuit.h(qubit)
        
            for qubit in range(qubit_count):
                circuit.x(qubit)
                
            for qubit in range(qubit_count-1):
                circuit.i(qubit)
        
            circuit.h(qubit_count-1)
            circuit.mct(list(range(qubit_count-1)), qubit_count-1)
            circuit.h(qubit_count-1)
            
            for qubit in range(qubit_count-1):
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

