from qiskit import QuantumCircuit


def qft(run_values, task_log):
    
    pass
        
    # input_period = run_values.get('period')
    # masquerade = run_values.get('masquerade')
    # masquerade_bool = masquerade.lower() == 'true'
    
    # period = ''.join('1' if digit == '1' else '0' for digit in input_period)
    
    # input_qubits_count = len(period)
    
    # output_qubits_count = input_qubits_count
    # all_qubits_count = input_qubits_count + output_qubits_count
    
    # input_qubits = range(input_qubits_count)
    # all_qubits = range(all_qubits_count)
    
    # measure_bits_count = input_qubits_count
    # measure_bits = range(measure_bits_count)


    # simon_oracle = build_simon_oracle(period, task_log, masquerade=masquerade_bool)
    

    # circuit = QuantumCircuit(all_qubits_count, measure_bits_count)
    
    # for input_qubit in input_qubits:    
    #     circuit.h(input_qubit)
        
    # circuit.append(simon_oracle, all_qubits)
        
    # for input_qubit in input_qubits:    
    #     circuit.h(input_qubit)
        

    # qubits_measurement_list = list(reversed(input_qubits))
    
    # circuit.measure(qubits_measurement_list, measure_bits)
    
    
    # task_log(f'SIMON input_period: {input_period}')
    # task_log(f'SIMON period: {period}')
    # task_log(f'SIMON masquerade: {masquerade}')
    # task_log(f'SIMON masquerade_bool: {masquerade_bool}')

    # task_log(f'SIMON input_qubits_count: {input_qubits_count}')
    # task_log(f'SIMON qubits_count: {all_qubits}')
    # task_log(f'SIMON qubits_measurement_list: {qubits_measurement_list}')
    
    # task_log(f'SIMON simon_oracle: \n{simon_oracle}')
    # task_log(f'SIMON circuit: \n{circuit}')
    
    # return circuit