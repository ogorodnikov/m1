# from math import gcd
# from random import randint

from math import log

from qiskit import Aer
from qiskit import QuantumCircuit

from core.algorithms.qft import build_qft_circuit

# from qft import build_qft_circuit


# MAX_EXPONENTIAL_BASE_PICKS = 10


class Shor:
    
    def shor(self, run_values, task_log):
        
        number_input = run_values.get('number')
        number = int(number_input)
        
        task_log(f'SHOR number: {number}')
        
        exponentiation_base = 7
        precision = 8
        
        circuit = self.estimate_phase(exponentiation_base, precision, task_log)
    
        circuit.name = 'Shor Circuit'
        
        task_log(f'SHOR circuit: \n{circuit}')
        
        return circuit
        

    def estimate_phase(self, exponentiation_base, precision, task_log):
        
        """ https://qiskit.org/textbook/ch-algorithms/shor.html """
        
        task_log(f'SHOR exponentiation_base: {exponentiation_base}')
        task_log(f'SHOR precision: {precision}')
        
        counting_qubits_count = precision
        measurement_bits_count = precision
        
        counting_qubits = range(counting_qubits_count)
        measurement_bits = range(measurement_bits_count)
        
        task_log(f'SHOR counting_qubits: {counting_qubits}')
        task_log(f'SHOR measurement_bits: {measurement_bits}')
        
        ancilla_qubits_count = int(log(precision, 2)) + 1
        
        task_log(f'SHOR ancilla_qubits_count: {ancilla_qubits_count}')
        
        ancilla_qubits = range(counting_qubits_count, 
                               counting_qubits_count + ancilla_qubits_count)

        task_log(f'SHOR ancilla_qubits: {ancilla_qubits}')
        
        register_qubit = counting_qubits_count + ancilla_qubits_count - 1

        task_log(f'SHOR register_qubit: {register_qubit}')
        
                                       
        circuit = QuantumCircuit(counting_qubits_count + ancilla_qubits_count, 
                                 counting_qubits_count)
                                 
        for counting_qubit in counting_qubits:
            circuit.h(counting_qubit)
            
        circuit.name = ''
        
        circuit.x(register_qubit)
        
        for camod_index in range(precision):
            
            task_log(f'SHOR camod_index: {camod_index}')
            
            circuit.append(self.controlled_amod15(exponentiation_base, 2**camod_index),
                           [camod_index] + [*ancilla_qubits])
        
        inverted_qft_circuit = build_qft_circuit(qubits_count=counting_qubits_count, 
                                                 inverted=True)
                                                 
        task_log(f'SHOR inverted_qft_circuit: \n{inverted_qft_circuit}')
            
        circuit.append(inverted_qft_circuit, counting_qubits)
        
        circuit.measure(counting_qubits, measurement_bits)
                           
        task_log(f'SHOR circuit: \n{circuit}')
        
        return circuit
        

    def controlled_amod15(self, exponentiation_base, power):
        
        camod_circuit = QuantumCircuit(4)        
        
        for iteration in range(power):
            
            if exponentiation_base in [2, 13]:
                camod_circuit.swap(0, 1)
                camod_circuit.swap(1, 2)
                camod_circuit.swap(2, 3)
                
            elif exponentiation_base in [7, 8]:
                camod_circuit.swap(2, 3)
                camod_circuit.swap(1, 2)
                camod_circuit.swap(0, 1)
                
            elif exponentiation_base == 11:
                camod_circuit.swap(1, 3)
                camod_circuit.swap(0, 2)
                
            if exponentiation_base in [7, 11, 13]:
                for q in range(4):
                    camod_circuit.x(q)
                    
        camod_gate = camod_circuit.to_gate()
        
        camod_gate.name = f"{exponentiation_base}^{power} mod 15"
        
        controlled_camod_gate = camod_gate.control()
        
        # task_log(f'SHOR camod_circuit: {camod_circuit}')  
        
        return controlled_camod_gate



# run_values = {'number': '330023'}

# Shor().shor(run_values)


def shor(run_values, task_log):
    
    return Shor().shor(run_values, task_log)
    
    
def shor_post_processing(run_result, task_log):
    
    counts = run_result.get_counts()
    
    task_log(f'SHOR run_result: {run_result}')
    task_log(f'SHOR counts: {counts}')