from qiskit import QuantumCircuit


# def build_dj_oracle(secret):
    
#     dj_oracle = QuantumCircuit(qubit_count)
#     dj_oracle.name = 'DJ Oracle'
    
    # return dj_oracle
    
    
def dj(run_values, task_log):
    
    full_secret = run_values.get('secret')
    secret_len = 2 ** int((len(full_secret).bit_length() + 1) ** 0.5)
    secret = full_secret[:secret_len]
    
    input_qubit_count = int(len(secret) ** 0.5)
    input_qubits = range(input_qubit_count)
    
    output_qubit = input_qubit_count
    
    qubit_count = input_qubit_count + 1
    qubits = range(qubit_count)
    
    measure_bit_count = input_qubit_count + 1
    measure_bits = range(measure_bit_count)
    
    states = range(secret_len)
    
    bin_template = f"0{input_qubit_count}b"
    
    truth_table = {f"{state:{bin_template}}": secret[state] for state in states}
    
    # mod2_truth_table = {f"{state:{bin_template}}": str(state % 2) for state in states}
    
    # inverted_states = set(truth_table.items()) - set(mod2_truth_table.items())
    
    
    # dj_oracle = build_dj_oracle(secret)

    circuit = QuantumCircuit(qubit_count, measure_bit_count)
    
    # for input_qubit in input_qubits:    
    #     circuit.h(input_qubit)
        
    # circuit.x(output_qubit)
    # circuit.h(output_qubit)
    
    # circuit.x(0)
    # circuit.x(1)
        
    circuit.barrier()
    
    # for input_qubit in input_qubits:    
    #     circuit.cx(input_qubit, output_qubit)
    
    circuit.barrier()
    
    for state, secret_digit in truth_table.items():
        
        if secret_digit == '0':
            continue
        
        for state_digit_index, state_digit in enumerate(state):
            if state_digit == '0':
                circuit.x(state_digit_index)
                
        circuit.mct(list(input_qubits), output_qubit)
        
        for state_digit_index, state_digit in enumerate(state):
            if state_digit == '0':
                circuit.x(state_digit_index)    

        circuit.barrier()
    
        
    # for input_qubit in input_qubits:    
    #     circuit.h(input_qubit)
        
        
    circuit.measure([2, 1, 0], measure_bits)


    task_log(f'DJ full_secret: {full_secret}')
    task_log(f'DJ secret: {secret}')
    task_log(f'DJ secret_len: {secret_len}')
    task_log(f'DJ qubit_count: {qubit_count}')
    
    task_log(f'DJ truth_table: {truth_table}')
    # task_log(f'DJ mod2_truth_table: {mod2_truth_table}')
    # task_log(f'DJ inverted_states: {inverted_states}')

    # task_log(f'DJ dj_oracle: \n{dj_oracle}')
    task_log(f'DJ circuit: \n{circuit}')
    

    return circuit