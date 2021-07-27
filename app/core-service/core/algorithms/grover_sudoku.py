from itertools import combinations, zip_longest

from qiskit import Aer, ClassicalRegister, QuantumRegister, QuantumCircuit, execute
from qiskit.tools.monitor import job_monitor


ONE_STATE = 0, 1
ZERO_STATE = 1, 0
MINUS_STATE = 2**-0.5, -(2**-0.5)


def build_sudoku_oracle(cells_count, pairs, sudoku_width):
    
    pairs_count = len(pairs)

    sudoku_oracle_circuit = QuantumCircuit(cells_count + pairs_count)

    for pair_index, pair in enumerate(pairs):
        
        (ax, ay), (bx, by) = pair
        
        a_index = ax + ay * sudoku_width
        b_index = bx + by * sudoku_width
        
        pair_qubit_index = pair_index + cells_count
        
        print((ax, ay), (bx, by), a_index, b_index, pair_qubit_index)
        
        sudoku_oracle_circuit.cx(a_index, pair_qubit_index)
        sudoku_oracle_circuit.cx(b_index, pair_qubit_index)
        
    sudoku_oracle_circuit.name = "Sudoku Oracle"
    
    return sudoku_oracle_circuit
    

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

    run_values = {'sudoku_width': '3',
                  'sudoku_height': '3',
                  'input_row_1': '',
                  'input_row_2': '',
                  'input_row_3': '',                  
                 }
                 

    sudoku_width = int(run_values.get('sudoku_width'))
    sudoku_height = int(run_values.get('sudoku_height'))
    
    # input_rows = [value.ljust(sudoku_width, '.')[:sudoku_width]
    #               for key, value in run_values.items()
    #               if 'input_row' in key]
                  
    # rows = input_rows[:sudoku_height]
    
    input_rows = [value for key, value in run_values.items() if 'input_row' in key]
    
    limited_rows = [row[:sudoku_width] for row in input_rows[:sudoku_height]]
    
    sudoku_rows = [row.ljust(sudoku_width, '.') for row in limited_rows]
    
    print(input_rows)
    print(limited_rows)
    print(sudoku_rows)

    cells_count = sudoku_height * sudoku_width
    
    row_pairs = sorted(((a, row_index), (b, row_index)) 
                       for a, b in combinations(range(sudoku_width), 2)
                       for row_index in range(sudoku_height))
                 
    column_pairs = sorted(((column_index, a), (column_index, b)) 
                          for a, b in combinations(range(sudoku_height), 2)
                          for column_index in range(sudoku_width))
    
    pairs = row_pairs + column_pairs
    
    row_pairs_count = len(row_pairs)
    column_pairs_count = len(column_pairs)
    pairs_count = len(pairs)
    
    
    for iterations in range(1, 3):
        
        print('>>>> Iterations:', iterations)
    
        cell_qubits = QuantumRegister(cells_count, name='c')
        pair_qubits = QuantumRegister(pairs_count, name='p')
        
        output_qubit = QuantumRegister(1, name='out')
        
        output_bits = ClassicalRegister(cells_count, name='b')
        
        circuit = QuantumCircuit(cell_qubits, pair_qubits, output_qubit, output_bits)
        
    
    
        for x in range(sudoku_width):
            for y in range(sudoku_height):
                
                cell_qubit = x + y * sudoku_width
                cell_input_value = sudoku_rows[y][x]
                
                if cell_input_value == '1':
                    circuit.initialize(ONE_STATE, cell_qubit)
                    
                elif cell_input_value == '0':
                    circuit.initialize(ZERO_STATE, cell_qubit)
                    
                else:
                    circuit.h(cell_qubit)      
    
        
        circuit.initialize(MINUS_STATE, output_qubit)
    
        
        sudoku_oracle = build_sudoku_oracle(cells_count, pairs, sudoku_width)
    
        elements_count = 2 ** cells_count
    
        repetitions =  (elements_count / pairs_count) ** 0.5 * 3.14 / 4
        repetitions_count = int(repetitions)
        
    
        
    
        for i in range(iterations):
        
            circuit.append(sudoku_oracle, range(cells_count + pairs_count))
            
            circuit.mct(pair_qubits, output_qubit)
            
            # circuit.append(sudoku_oracle, range(cells_count + pairs_count))
            
            diffuser = build_diffuser(cells_count)
            
            circuit.append(diffuser, cell_qubits)
    
    
        # measure
        
        circuit.measure(cell_qubits, output_bits)
        
            
        print(f'SUDOKU run_values: {run_values}')
        print(f'SUDOKU input_rows: {input_rows}')    
        print(f'SUDOKU sudoku_rows: {sudoku_rows}')
        print(f'SUDOKU row_pairs: {row_pairs}')
        print(f'SUDOKU column_pairs: {column_pairs}')
        print(f'SUDOKU pairs: {pairs}')
        
        print(f'SUDOKU cells_count: {cells_count}')        
        print(f'SUDOKU pairs_count: {pairs_count}')
        
        print(f'SUDOKU elements_count: {elements_count}')
        print(f'SUDOKU repetitions: {repetitions}')
        print(f'SUDOKU repetitions_count: {repetitions_count}')
        
        print(f'SUDOKU sudoku_oracle: \n{sudoku_oracle}')
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