from qiskit import QuantumCircuit


# def build_dj_oracle(secret):
    
#     dj_oracle = QuantumCircuit(qubit_count)
#     dj_oracle.name = 'DJ Oracle'
    
    # return dj_oracle
    
    
def dj(run_values, task_log):
    
    full_secret = run_values.get('secret')
    secret_len = 2 ** int(len(full_secret) ** 0.5)
    secret = full_secret[:secret_len]
    
    input_qubit_count = int(len(secret) ** 0.5)
    input_qubits = range(input_qubit_count)
    
    output_qubit = input_qubit_count
    
    qubit_count = input_qubit_count + 1
    qubits = range(qubit_count)
    
    measure_bit_count = input_qubit_count
    measure_bits = range(measure_bit_count)
    
    states = range(secret_len)
    
    bin_template = f"0{input_qubit_count}b"
    
    truth_table = {f"{state:{bin_template}}": secret[state] for state in states}
    
    mod2_truth_table = {f"{state:{bin_template}}": str(state % 2) for state in states}
    
    inverted_states = set(truth_table.items()) - set(mod2_truth_table.items())
    
    
    # dj_oracle = build_dj_oracle(secret)

    circuit = QuantumCircuit(qubit_count, measure_bit_count)
    
    
    
    for input_qubit in input_qubits:    
        circuit.cx(input_qubit, output_qubit)
    
    
    circuit.barrier()
    
    for state, _ in sorted(inverted_states):
        
        for qubit, value in enumerate(state):
            if value == '0':
                circuit.x(qubit)
                
        circuit.mct(list(input_qubits), output_qubit)
        
        for qubit, value in enumerate(state):
            if value == '0':
                circuit.x(qubit)        

        circuit.barrier()   
    
    # circuit.x(output_qubit_index)
    
    # for qubit_index in range(qubit_count):    
    #     circuit.h(qubit_index)    
    
    # circuit.append(dj_oracle, range(qubit_count))
    
    # for qubit_index in input_qubits:    
    #     circuit.h(qubit_index)
        
        
    circuit.measure(input_qubits, measure_bits)
    

    task_log(f'DJ full_secret: {full_secret}')
    task_log(f'DJ secret: {secret}')
    task_log(f'DJ qubit_count: {qubit_count}')
    
    task_log(f'DJ truth_table: {truth_table}')
    task_log(f'DJ mod2_truth_table: {mod2_truth_table}')
    task_log(f'DJ inverted_states: {inverted_states}')

    # task_log(f'DJ dj_oracle: \n{dj_oracle}')
    task_log(f'DJ circuit: \n{circuit}')
    

    return circuit