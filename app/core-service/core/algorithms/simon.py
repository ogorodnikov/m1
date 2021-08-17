from qiskit import QuantumCircuit


def build_simon_oracle(period, masquerade=True):
    
    input_qubits_count = len(period)
    output_qubits_count = input_qubits_count
    qubits_count = input_qubits_count + output_qubits_count
    
    input_qubits = range(input_qubits_count)
    output_qubits = range(output_qubits_count)
    qubits = range(qubits_count)
    
    oracle = QuantumCircuit(qubits_count)
    oracle.name = 'Simon Oracle'
    
    
    for input_qubit, output_qubit in zip(input_qubits, output_qubits):
        
        oracle.cx(input_qubit, output_qubit)
        
    
    is_one_to_one_mapping = '1' in period
    
    if is_one_to_one_mapping:
        
        return oracle
        
    
    first_period_one_bit = period.find('1')
    
    for output_qubit, digit in enumerate(period, input_qubits_count):
        
        if digit == '1':
            
            oracle.cx(first_period_one_bit, output_qubit)
        
    return oracle
    
    if masquerade:
        
        oracle.barrier()
    

def simon(run_values, task_log):
        
    input_period = run_values.get('period')
    
    period = ''.join('1' if digit == '1' else '0' for digit in input_period)
    
    input_qubits_count = len(period)
    
    output_qubits_count = input_qubits_count
    qubits_count = input_qubits_count + output_qubits_count
    
    input_qubits = range(input_qubits_count)
    qubits = range(qubits_count)
    
    measure_bits_count = input_qubits_count
    measure_bits = range(measure_bits_count)


    simon_oracle = build_simon_oracle(period)
    

    circuit = QuantumCircuit(qubits_count, measure_bits_count)
    
    for input_qubit in input_qubits:    
        circuit.h(input_qubit)
        
    circuit.append(simon_oracle, all_qubits)
        
    for input_qubit in input_qubits:    
        circuit.h(input_qubit)
        
#     circuit.barrier()

    qubits_measurement_list = list(reversed(input_qubits))
    
    circuit.measure(qubits_measurement_list, measure_bits)
    
    
    task_log(f'SIMON input_period: {input_period}')
    task_log(f'SIMON period: {period}')

    task_log(f'SIMON input_qubits_count: {input_qubits_count}')
    task_log(f'SIMON all_qubits_count: {all_qubits_count}')
    task_log(f'SIMON qubits_measurement_list: {qubits_measurement_list}')
    
    task_log(f'SIMON simon_oracle: {simon_oracle}')
    task_log(f'SIMON circuit: \n{circuit}')
    
#     task_log(f'SIMON if majority of counts is all 0 - secret is constant')
#     task_log(f'SIMON if majority of counts is any other state - secret is balanced')
#     task_log(f'SIMON if counts are distributed via multiple states - probably secret is unbalanced')
    

    return circuit