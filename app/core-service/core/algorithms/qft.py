from math import pi
from itertools import combinations_with_replacement

from qiskit import QuantumCircuit


def build_qft_circuit(qubits_count, task_log):
    
    qubits = range(qubits_count)
    pairs = combinations_with_replacement(qubits, 2)
    
    circuit = QuantumCircuit(qubits_count)
    circuit.name = 'QFT Circuit'    
    
    for control_qubit, target_qubit in pairs:
        
        if control_qubit == target_qubit:
            circuit.barrier()
            circuit.h(control_qubit)
            
        else:
            distance = abs(control_qubit - target_qubit)
            theta = pi / 2 ** distance
            circuit.cp(theta, control_qubit, target_qubit)
            
            task_log(f'QFT distance: {distance}')
            task_log(f'QFT theta: {theta}')
            
        task_log(f'QFT control_qubit: {control_qubit}')
        task_log(f'QFT target_qubit: {target_qubit}')
        task_log(f'QFT circuit: \n{circuit}')
    
    
    # if qubit_index == qubits_count:
    #     return
    
    # circuit = QuantumCircuit(qubits_count)

    # circuit.h(qubit_index)
    
    # for target_qubit in range(qubit_index + 1, qubits_count):

    #     task_log(f'QFT qubit_index: {qubit_index}')
    #     task_log(f'QFT target_qubit: {target_qubit}')
        
    #     theta = pi / 2 ** target_qubit
        
    #     circuit.cp(theta, qubit_index, target_qubit)

    #     task_log(f'QFT theta: {theta}')
    #     task_log(f'QFT circuit: \n{circuit}')
        
    
    # next_circuit_part = build_qft_circuit(qubits_count, task_log, qubit_index + 1)
    
    # if next_circuit_part:

    #     task_log(f'QFT qargs: {list(range(qubit_index, qubits_count))}')       
        
    #     circuit.append(next_circuit_part, qargs=range(qubit_index, qubits_count))
    
    return circuit
    
    

def qft(run_values, task_log):
    
    input_number = run_values.get('number')

    number = ''.join('1' if digit == '1' else '0' for digit in input_number)
    
    qubits_count = len(number)
    qubits = range(qubits_count)
    
    measure_bits_count = qubits_count
    measure_bits = range(measure_bits_count)


    circuit = build_qft_circuit(qubits_count, task_log)
    

    # circuit = QuantumCircuit(all_qubits_count, measure_bits_count)
    
    # for input_qubit in input_qubits:    
    #     circuit.h(input_qubit)
        
    # circuit.append(simon_oracle, all_qubits)
        
    # for input_qubit in input_qubits:    
    #     circuit.h(input_qubit)
        

    # qubits_measurement_list = list(reversed(qubits))
    
    # circuit.measure(qubits_measurement_list, measure_bits)
    
    
    task_log(f'QFT input_number: {input_number}')
    task_log(f'QFT number: {number}')
    task_log(f'QFT qubits_count: {qubits_count}')

    task_log(f'QFT circuit: \n{circuit}')
    
    
    return circuit