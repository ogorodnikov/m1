from qiskit import QuantumCircuit


def build_dj_oracle(secret):
    
    qubit_count = len(secret)
    
    output_qubit_index = qubit_count - 1
    
    dj_oracle = QuantumCircuit(qubit_count)
    dj_oracle.name = 'DJ Oracle'
    
    for input_qubit_index, digit in enumerate(reversed(secret)):
        if digit == '1':
            dj_oracle.x(input_qubit_index)
            
    dj_oracle.barrier()
            
    for input_qubit_index in range(qubit_count - 1):    
        dj_oracle.cx(input_qubit_index, output_qubit_index)
        
    dj_oracle.barrier()
        
    for input_qubit_index, digit in enumerate(reversed(secret)):
        if digit == '1':
            dj_oracle.x(input_qubit_index)
    
    return dj_oracle
    
    
def dj(run_values, task_log):
    
    full_secret = run_values.get('secret')
    
    secret_len = 2 ** int(len(full_secret) ** 0.5)
    
    secret = full_secret[:secret_len]
    
    qubit_count = len(secret)
    measure_bit_count = qubit_count - 1
    
    input_qubits = range(qubit_count - 1)
    measure_bits = range(measure_bit_count)
    
    output_qubit_index = qubit_count - 1
    
    
    dj_oracle = build_dj_oracle(secret)

    circuit = QuantumCircuit(qubit_count, measure_bit_count)
    
    
    circuit.x(output_qubit_index)
    
    for qubit_index in range(qubit_count):    
        circuit.h(qubit_index)    
    
    circuit.append(dj_oracle, range(qubit_count))
    
    for qubit_index in input_qubits:    
        circuit.h(qubit_index)
        
        
    circuit.measure(input_qubits, measure_bits)
    

    task_log(f'DJ full_secret: {full_secret}')
    task_log(f'DJ secret: {secret}')
    task_log(f'DJ qubit_count: {qubit_count}')

    task_log(f'DJ dj_oracle: \n{dj_oracle}')
    task_log(f'DJ circuit: \n{circuit}')
    

    return circuit