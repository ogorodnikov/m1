from math import pi
from itertools import combinations_with_replacement

from qiskit import QuantumCircuit

from qiskit import Aer


def append_qft_circuit(circuit, qubits_count, task_log):
    
    qubits = range(qubits_count)
    pairs = combinations_with_replacement(qubits, 2)
    
    # circuit = QuantumCircuit(qubits_count)
    # circuit.name = 'QFT Circuit'    
    
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
    
    # return circuit
    
    

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
            
    append_qft_circuit(circuit, qubits_count, task_log)
        
    # circuit.append(qft_circuit, qubits)
        
    # for input_qubit in input_qubits:    
    #     circuit.h(input_qubit)
        

    # qubits_measurement_list = list(reversed(qubits))
    
    # circuit.measure(qubits_measurement_list, measure_bits)
    
    backend = Aer.get_backend("qasm_simulator")
    
    circuit_copy = circuit.copy()
    circuit_copy.save_statevector()
    
    statevector = backend.run(circuit_copy).result().get_statevector()

    
    task_log(f'QFT input_number: {input_number}')
    task_log(f'QFT number: {number}')
    task_log(f'QFT qubits_count: {qubits_count}')

    task_log(f'QFT circuit: \n{circuit}')
    
    task_log(f'QFT statevector: {statevector}')
    
    for state in statevector:
        
        task_log(f'QFT state: {state:.2f}')
    
    
    
    return circuit