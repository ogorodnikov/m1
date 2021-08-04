from qiskit import QuantumCircuit


# def build_dj_oracle(secret):
    
#     qubit_count = len(secret) ** 0.5
    
#     input_qubits = range(qubit_count - 1)
#     output_qubit = qubit_count - 1
    
#     # int_to_bin_template = 
    
#     truth_table = {f"{state:0{qubit_count}b}": secret[state] for state in input_qubits}
    
#     print(truth_table)
    
    
#     dj_oracle = QuantumCircuit(qubit_count)
#     dj_oracle.name = 'DJ Oracle'
    
#     for input_qubit in input_qubits:
#         dj_oracle.cx(input_qubit, output_qubit)
    
    
    
    
    # for input_qubit_index, digit in enumerate(reversed(secret)):
    #     if digit == '1':
    #         dj_oracle.x(input_qubit_index)
            
    # dj_oracle.barrier()
            
    # for input_qubit_index in range(qubit_count - 1):    
    #     dj_oracle.cx(input_qubit_index, output_qubit_index)
        
    # dj_oracle.barrier()
        
    # for input_qubit_index, digit in enumerate(reversed(secret)):
    #     if digit == '1':
    #         dj_oracle.x(input_qubit_index)
    
    # return dj_oracle
    
    
def dj(run_values, task_log):
    
    full_secret = run_values.get('secret')
    secret_len = 2 ** int(len(full_secret) ** 0.5)
    secret = full_secret[:secret_len]
    
    input_qubit_count = int(len(secret) ** 0.5)
    input_qubits = range(input_qubit_count)
    
    output_qubit_index = input_qubit_count
    
    qubit_count = input_qubit_count + 1
    qubits = range(qubit_count)
    
    measure_bit_count = input_qubit_count
    measure_bits = range(measure_bit_count)
    
    #     # int_to_bin_template =
    
    states = range(secret_len)
    
    truth_table = {f"{state:0{input_qubit_count}b}": secret[state] for state in states}
    
    
    # dj_oracle = build_dj_oracle(secret)

    circuit = QuantumCircuit(qubit_count, measure_bit_count)
    
    
    # circuit.x(output_qubit_index)
    
    # for qubit_index in range(qubit_count):    
    #     circuit.h(qubit_index)    
    
    # circuit.append(dj_oracle, range(qubit_count))
    
    # for qubit_index in input_qubits:    
    #     circuit.h(qubit_index)
        
        
    # circuit.measure(input_qubits, measure_bits)
    

    task_log(f'DJ full_secret: {full_secret}')
    task_log(f'DJ secret: {secret}')
    task_log(f'DJ qubit_count: {qubit_count}')
    task_log(f'DJ truth_table: {truth_table}')

    # task_log(f'DJ dj_oracle: \n{dj_oracle}')
    task_log(f'DJ circuit: \n{circuit}')
    

    return circuit