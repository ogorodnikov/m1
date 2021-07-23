from qiskit import *
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import backend_overview, job_monitor


# from qiskit_textbook.problems import grover_problem_oracle



def grover(run_values):
    
    qubit_count = 4
    patterns = (2, 1), #(0, 2)
    
    circuit = QuantumCircuit(qubit_count)
    
    for qubit in range(qubit_count):
        circuit.h(qubit)
    
    for pattern in patterns:
        circuit.cz(*pattern)
    
    elements_count = 2 ** qubit_count
    patterns_count = len(patterns)
    
    repetitions =  (elements_count / patterns_count) ** 0.5 * 3.14 / 4
    repetitions_count = int(repetitions)
    
    print(f'GROVER elements_count: {elements_count}')
    print(f'GROVER repetitions: {repetitions}')
    print(f'GROVER repetitions_count: {repetitions_count}')
    
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
    
    print(circuit)
    
    
    # run
    
    backend = Aer.get_backend('qasm_simulator')
    
    job = execute(circuit, backend=backend, shots=1000)
    
    result = job.result()
    
    counts = result.get_counts()
    
    
    # oracle = grover_problem_oracle(8, variant=10, print_solutions=True)

    return counts
    
result = grover('11')

[print(f'{state}: {count}') for state, count in sorted(result.items())]