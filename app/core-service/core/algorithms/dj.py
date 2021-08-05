from qiskit import QuantumCircuit


def build_truth_table_oracle(truth_table, task_log):
    
    
    input_qubits_count = len(next(iter(truth_table)))
    input_qubits = range(input_qubits_count)

    all_qubits_count = input_qubits_count + 1
    
    output_qubit = all_qubits_count - 1
    
    
    oracle = QuantumCircuit(all_qubits_count)
    oracle.name = 'Truth Table Oracle'
    
    
    for state, secret_digit in truth_table.items():
        
        if secret_digit == '0':
            continue
        
        for state_digit_index, state_digit in enumerate(state):
            if state_digit == '0':
                oracle.x(state_digit_index)
                
        oracle.mct(list(input_qubits), output_qubit)
        
        for state_digit_index, state_digit in enumerate(state):
            if state_digit == '0':
                oracle.x(state_digit_index)    

        oracle.barrier()
        
    
    return oracle
    
    
def dj(run_values, task_log):
    
    input_secret = run_values.get('secret')
    
    full_secret = ''.join('1' if digit == '1' else '0' for digit in input_secret)
    
    secret_bit_len = (len(full_secret) - 1).bit_length()
    
    secret_len = 2 ** secret_bit_len
        
    secret = full_secret.ljust(secret_len, '0')[:secret_len]
    
    input_qubits_count = secret_bit_len
    input_qubits = range(input_qubits_count)
    
    all_qubits_count = input_qubits_count + 1
    all_qubits = range(all_qubits_count)
    
    output_qubit = input_qubits_count
    
    measure_bits_count = input_qubits_count
    measure_bits = range(measure_bits_count)

    
    states = range(secret_len)
    
    bin_template = f"0{input_qubits_count}b"
    
    truth_table = {f"{state:{bin_template}}": secret[state] for state in states}
    
    
    truth_table_oracle = build_truth_table_oracle(truth_table, task_log)
    

    circuit = QuantumCircuit(all_qubits_count, measure_bits_count)
    
    for input_qubit in input_qubits:    
        circuit.h(input_qubit)
        
    circuit.x(output_qubit)
    circuit.h(output_qubit)
    

    circuit.append(truth_table_oracle, all_qubits)
    
        
    for input_qubit in input_qubits:    
        circuit.h(input_qubit)
        
    circuit.barrier()
        

    qubits_measurement_list = list(reversed(input_qubits))
    
    circuit.measure(qubits_measurement_list, measure_bits)
    
    
    task_log(f'DJ input_secret: {input_secret}')
    task_log(f'DJ full_secret: {full_secret}')
    task_log(f'DJ secret: {secret}')
    task_log(f'DJ secret_bit_len: {secret_bit_len}')
    task_log(f'DJ secret_len: {secret_len}')
    
    task_log(f'DJ input_qubits_count: {input_qubits_count}')
    task_log(f'DJ all_qubits_count: {all_qubits_count}')
    task_log(f'DJ output_qubit: {output_qubit}')
    task_log(f'DJ qubits_measurement_list: {qubits_measurement_list}')
    
    task_log(f'DJ truth_table: {truth_table}')
    task_log(f'DJ truth_table_oracle: \n{truth_table_oracle}')
    task_log(f'DJ circuit: \n{circuit}')
    
    task_log(f'DJ if majority of counts is all 0 - secret is constant')
    task_log(f'DJ if majority of counts is any other state - secret is balanced')
    task_log(f'DJ if counts are distributed via multiple states - probably secret is unbalanced')
    

    return circuit