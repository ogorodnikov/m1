from itertools import combinations, zip_longest

from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit



def grover_sudoku(run_values):
    
    run_mode = 'simulator'
    # run_mode = 'quantum_device'

    run_values = {'secret_row_1': '011',
                  'secret_row_2': '1',
                  'secret_row_3': '10',
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


    print(f'SUDOKU run_values: {run_values}')
    print(f'SUDOKU secrets: {secrets}')    
    print(f'SUDOKU rows: {rows}')
    print(f'SUDOKU columns: {columns}')
    print(f'SUDOKU row_pairs: {row_pairs}')
    print(f'SUDOKU column_pairs: {column_pairs}')
    print(f'SUDOKU pairs: {pairs}')
    print(f'SUDOKU circuit: /n{circuit}')
    
    quit()



    print(f'SUDOKU elements_count: {elements_count}')
    
    quit()

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
    

    ###   Run   ###

    if run_mode == 'simulator':
        
        backend = Aer.get_backend('qasm_simulator')
        
        
    if run_mode == 'quantum_device':
    
        qiskit_token = app.config.get('QISKIT_TOKEN')
        IBMQ.save_account(qiskit_token)
        
        if not IBMQ.active_account():
            IBMQ.load_account()
            
        provider = IBMQ.get_provider()
        
        app.logger.info(f'GROVER provider: {provider}')
        app.logger.info(f'GROVER provider.backends(): {provider.backends()}')
        
        # backend = provider.get_backend('ibmq_manila')

        backend = get_least_busy_backend(provider, qubit_count)
        

    app.logger.info(f'GROVER run_mode: {run_mode}')
    app.logger.info(f'GROVER backend: {backend}')


    job = execute(circuit, backend=backend, shots=1024)
    
    job_monitor(job, interval=5)
    
    result = job.result()
    
    counts = result.get_counts()
    
    app.logger.info(f'GROVER counts:')
    [app.logger.info(f'{state}: {count}') for state, count in sorted(counts.items())]

    return {'Counts:': counts}


grover_sudoku('monya')