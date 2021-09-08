from math import pi
from itertools import combinations_with_replacement

from qiskit import QuantumCircuit
from qiskit import Aer

from core.algorithms.qft import build_qft_circuit


def qpe(run_values, task_log):
    
    theta = run_values.get('theta')
    precision = run_values.get('precision')

    counting_qubits_count = int(precision)
    counting_qubits = range(counting_qubits_count)
    
    eigenstate_qubit = max(counting_qubits) + 1
    qubits_count = counting_qubits_count + 1
    
    measure_bits_count = counting_qubits_count
    measure_bits = range(measure_bits_count)

    circuit = QuantumCircuit(qubits_count, measure_bits_count)
    circuit.name = 'QPE Circuit'
    
    for counting_qubit in counting_qubits:
        circuit.h(counting_qubit)
        
    circuit.x(eigenstate_qubit)
    
    # for input_qubit, digit in enumerate(number):
        
    #     if digit == '1':
    #         circuit.x(input_qubit)
            

    # qft_circuit = build_qft_circuit(qubits_count)
    
    # circuit.append(qft_circuit, qubits)
    
    # iqft_circuit = qft_circuit.inverse()
    # iqft_circuit.name = 'IQFT Circuit'

    # task_log(f'QFT input_number: {input_number}')
    # task_log(f'QFT number: {number}')
    # task_log(f'QFT qubits_count: {qubits_count}')

    task_log(f'QFT circuit: \n{circuit}')

    return circuit