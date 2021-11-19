from qiskit import QuantumCircuit


def build_truth_table_oracle(truth_table) -> QuantumCircuit:
    
    """
    Create Oracle quantum circuit for input truth table.
    
    - for each row of input truth table:
      if output is 1:
      flip each input qubit which is 0 in input state
      
    Example:
    
      Truth table:
      
      00: 1
      01: 0
      10: 1
      11: 0
      
      Input states: 00, 01, 10, 11
      Outputs: 1, 0, 1, 0
     
    Actions:
    
      00: 1 -> Output is 1 -> Both input qubits are 0 -> Flip both input qubits
      01: 0 -> Output is 0 -> Nothing
      10: 1 -> Output is 1 -> 2nd input qubit is 0 -> Flip only 2nd input qubit
      11: 0 -> Output is 0 -> Nothing
    
    """
    
    
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
    
    
def dj(run_values, task_log) -> QuantumCircuit:

    """
    Create Deutch-Jozsa quantum circuit for input 'secret' value:
    
    - get 'secret' from input run values
    - convert 'secret' to string of '1' and '0'
    - fill 'secret' with '0' up to integer power of 2:
    
      101    -> 1010
      1010   -> 1010
      10101  -> 10101000
      101010 -> 10101000
    
    - create truth table from input 'secret':
    
      'Secret': String of '1' and '0':
      
      1010
      
      Truth table: Each output is '1' or '0' from input 'secret':
      
      00: 1
      01: 0
      10: 1
      11: 0
      
    - create Oracle quantum circuit for truth table
    - apply H and X gates to Oracle
    - measure qubits
    
    Results:
    
    - if majority of counts in 'all 0' state:
      
      secret is constant
      
    - if majority of counts in not 'all 0' state:
    
      secret is balanced
      
    - if counts are distributed via multiple states:
    
      probably secret is unbalanced
      
    Example:
    
      1)
    
      Input 'secret': 1111
      Counts: {'00': 1024}
      
      ->
      
      Majority of counts in 'all 0' state '00': 
    
      Secret is constant     

      2)
    
      Input 'secret': 1010
      Counts: {'01': 1024}
      
      ->
      
      Majority of counts in not 'all 0' state '01': 
    
      Secret is balanced
      
    """
    
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
    
    
    truth_table_oracle = build_truth_table_oracle(truth_table)
    

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