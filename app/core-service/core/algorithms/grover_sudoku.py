from itertools import combinations, zip_longest

from qiskit import Aer, ClassicalRegister, QuantumRegister, QuantumCircuit, execute
from qiskit.tools.monitor import job_monitor


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
    

def grover_sudoku(run_values):
    
    run_mode = 'simulator'
    # run_mode = 'quantum_device'

    run_values = {'secret_row_1': '10',
                  'secret_row_2': '0',
                #   'secret_row_3': '10',
                 }
                 
    
    secrets = [value for key, value in run_values.items() if 'secret_row' in key]

    columns = list(zip_longest(*secrets, fillvalue='0'))
    rows = list(zip(*columns))
    
    height = len(rows)
    width = len(columns)
    cells_count = height * width
    
    row_pairs = sorted(((a, row_index), (b, row_index)) 
                       for a, b in combinations(range(width), 2)
                       for row_index in range(height))
                 
    column_pairs = sorted(((column_index, a), (column_index, b)) 
                          for a, b in combinations(range(height), 2)
                          for column_index in range(width))
    
    pairs = row_pairs + column_pairs
    
    row_pairs_count = len(row_pairs)
    column_pairs_count = len(column_pairs)
    pairs_count = len(pairs)
    
    cell_qubits = QuantumRegister(cells_count, name='c')
    pair_qubits = QuantumRegister(pairs_count, name='p')
    output_qubit = QuantumRegister(1, name='out')
    bits = ClassicalRegister(cells_count, name='b')
    circuit = QuantumCircuit(cell_qubits, pair_qubits, output_qubit, bits)
    

    
    one_state = (0, 1)
    
    for x in range(width):
        
        for y in range(height):
            
            cell_qubit = x + y * width
            
            if rows[y][x] == '1':
                
                circuit.initialize(one_state, cell_qubit)
                
            else:
                
                circuit.h(cell_qubit)      
        
        
    
    minus_state = (1 / 2**0.5, -1 / 2**0.5)
    
    circuit.initialize(minus_state, output_qubit)
    

    
    # circuit.h(range(1, cells_count))

    
    sudoku_oracle_circuit = QuantumCircuit(cells_count + pairs_count)

    for pair_index, pair in enumerate(pairs):
        
        (ax, ay), (bx, by) = pair
        
        a_index = ax + ay * width
        b_index = bx + by * width
        
        pair_qubit_index = pair_index + cells_count
        
        print((ax, ay), (bx, by), a_index, b_index, pair_qubit_index)
        
        sudoku_oracle_circuit.cx(a_index, pair_qubit_index)
        sudoku_oracle_circuit.cx(b_index, pair_qubit_index)
        
    sudoku_oracle_gate = sudoku_oracle_circuit.to_gate()
    sudoku_oracle_gate.name = "Sudoku Oracle"
    
    
    elements_count = cells_count ** 2

    repetitions =  (elements_count / pairs_count) ** 0.5 * 3.14 / 4
    repetitions_count = int(repetitions)
    
    print(f'SUDOKU elements_count: {elements_count}')
    print(f'SUDOKU pairs_count: {pairs_count}')
    print(f'SUDOKU repetitions: {repetitions}')
    print(f'SUDOKU repetitions_count: {repetitions_count}')
    
    quit()
    

    for i in range(repetitions_count):
    
        circuit.append(sudoku_oracle_gate, range(cells_count + pairs_count))
        
        circuit.mct(pair_qubits, output_qubit)
        
        circuit.append(sudoku_oracle_gate, range(cells_count + pairs_count))
        
        diffuser = build_diffuser(cells_count)
        
        circuit.append(diffuser, cell_qubits)


    # measure
    
    circuit.measure(cell_qubits, bits)
    
        
    print(f'SUDOKU run_values: {run_values}')
    print(f'SUDOKU secrets: {secrets}')    
    print(f'SUDOKU rows: {rows}')
    print(f'SUDOKU columns: {columns}')
    print(f'SUDOKU row_pairs: {row_pairs}')
    print(f'SUDOKU column_pairs: {column_pairs}')
    print(f'SUDOKU pairs: {pairs}')
    print(f'SUDOKU circuit: \n{circuit}')


    ###   Run   ###

    if run_mode == 'simulator':
        
        backend = Aer.get_backend('qasm_simulator')
        
        
    if run_mode == 'quantum_device':
    
        qiskit_token = app.config.get('QISKIT_TOKEN')
        IBMQ.save_account(qiskit_token)
        
        if not IBMQ.active_account():
            IBMQ.load_account()
            
        provider = IBMQ.get_provider()
        
        print(f'SUDOKU provider: {provider}')
        print(f'SUDOKU provider.backends(): {provider.backends()}')
        
        # backend = provider.get_backend('ibmq_manila')

        backend = get_least_busy_backend(provider, qubit_count)
        

    print(f'SUDOKU run_mode: {run_mode}')
    print(f'SUDOKU backend: {backend}')


    job = execute(circuit, backend=backend, shots=1024)
    
    job_monitor(job, interval=5)
    
    result = job.result()
    
    counts = result.get_counts()
    
    print(f'SUDOKU counts:')
    [print(f'{state}: {count}') for state, count in sorted(counts.items())]

    return {'Counts:': counts}


grover_sudoku('monya')