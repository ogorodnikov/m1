from math import pi
from itertools import combinations_with_replacement

from qiskit import QuantumCircuit

from qiskit import Aer

from qiskit.visualization import plot_bloch_multivector


def append_qft_circuit(circuit, inverted=False):
    
    qubits_count = circuit.num_qubits
    qubits = range(qubits_count)
    
    qubit_pairs = combinations_with_replacement(qubits, 2)
    
    pairs = reversed(tuple(qubit_pairs)) if inverted else qubit_pairs

    for control_qubit, target_qubit in pairs:
        
        if control_qubit == target_qubit:
            circuit.barrier()
            circuit.h(control_qubit)
            
        else:
            distance = abs(control_qubit - target_qubit)
            theta = pi / 2 ** distance
            circuit.cp(theta, control_qubit, target_qubit)
            
        #     task_log(f'QFT distance: {distance}')
        #     task_log(f'QFT theta: {theta}')
            
        # task_log(f'QFT control_qubit: {control_qubit}')
        # task_log(f'QFT target_qubit: {target_qubit}')
        # task_log(f'QFT circuit: \n{circuit}')
        


def qft(run_values, task_log):
    
    input_number = run_values.get('number')

    number = ''.join('1' if digit == '1' else '0' for digit in input_number)
    
    qubits_count = len(number)
    qubits = range(qubits_count)
    
    measure_bits_count = qubits_count
    measure_bits = range(measure_bits_count)

    circuit = QuantumCircuit(qubits_count, measure_bits_count)
    circuit.name = 'QFT Circuit'
    
    for input_qubit, digit in enumerate(number):
        
        if digit == '1':
            circuit.x(input_qubit)
            
    append_qft_circuit(circuit)
        

    task_log(f'QFT input_number: {input_number}')
    task_log(f'QFT number: {number}')
    task_log(f'QFT qubits_count: {qubits_count}')

    task_log(f'QFT circuit: \n{circuit}')
    
    
    inverted_circuit = circuit.inverse()
    
    task_log(f'QFT inverted_circuit: \n{inverted_circuit}')
    

    # append_qft_circuit(circuit, inverted=True)
    
    # qubits_measurement_list = list(reversed(qubits))
    # circuit.measure(qubits_measurement_list, measure_bits)

    
    return circuit