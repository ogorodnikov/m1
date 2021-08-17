from qiskit import QuantumCircuit


def build_simon_oracle(period, masquerade=True):
    
    input_qubits_count = len(period)
    
    output_qubits_count = input_qubits_count
    qubits_count = input_qubits_count + output_qubits_count
    
    input_qubits = range(input_qubits_count)
    qubits = range(qubits_count)
    
    oracle = QuantumCircuit(qubits_count)
    oracle.name = 'Simon Oracle'
    
    
    
#     for state, secret_digit in truth_table.items():
        
#         if secret_digit == '0':
#             continue
        
#         for state_digit_index, state_digit in enumerate(state):
#             if state_digit == '0':
#                 oracle.x(state_digit_index)
                
#         oracle.mct(list(input_qubits), output_qubit)
        
#         for state_digit_index, state_digit in enumerate(state):
#             if state_digit == '0':
#                 oracle.x(state_digit_index)    

#         oracle.barrier()
        
    
#     return oracle
    
    
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


#     simon_oracle = build_simon_oracle(period, task_log)
    

#     circuit = QuantumCircuit(all_qubits_count, measure_bits_count)
    
#     for input_qubit in input_qubits:    
#         circuit.h(input_qubit)
        
#     circuit.x(output_qubit)
#     circuit.h(output_qubit)
    

#     circuit.append(truth_table_oracle, all_qubits)
    
        
#     for input_qubit in input_qubits:    
#         circuit.h(input_qubit)
        
#     circuit.barrier()
        

#     qubits_measurement_list = list(reversed(input_qubits))
    
#     circuit.measure(qubits_measurement_list, measure_bits)
    
    
#     task_log(f'DJ input_secret: {input_secret}')
#     task_log(f'DJ full_secret: {full_secret}')
#     task_log(f'DJ secret: {secret}')
#     task_log(f'DJ secret_bit_len: {secret_bit_len}')
#     task_log(f'DJ secret_len: {secret_len}')
    
#     task_log(f'DJ input_qubits_count: {input_qubits_count}')
#     task_log(f'DJ all_qubits_count: {all_qubits_count}')
#     task_log(f'DJ output_qubit: {output_qubit}')
#     task_log(f'DJ qubits_measurement_list: {qubits_measurement_list}')
    
#     task_log(f'DJ truth_table: {truth_table}')
#     task_log(f'DJ truth_table_oracle: \n{truth_table_oracle}')
#     task_log(f'DJ circuit: \n{circuit}')
    
#     task_log(f'DJ if majority of counts is all 0 - secret is constant')
#     task_log(f'DJ if majority of counts is any other state - secret is balanced')
#     task_log(f'DJ if counts are distributed via multiple states - probably secret is unbalanced')
    

#     return circuit