from math import gcd
from math import log

from fractions import Fraction

from qiskit import QuantumCircuit

from qft import build_qft_circuit


class Shor:
    
    def shor(self, run_values, task_log):
        
        number_input = run_values.get('number')
        precision_input = run_values.get('precision')
        exponentiation_base_input = run_values.get('exponentiation_base')
        
        number = int(number_input)
        precision = int(precision_input)
        exponentiation_base = int(exponentiation_base_input)
        
        task_log(f'SHOR number: {number}')
        task_log(f'SHOR precision: {precision}')
        task_log(f'SHOR exponentiation_base: {exponentiation_base}')
        
        circuit = self.estimate_phase(exponentiation_base, number, precision, task_log)
        circuit.name = 'Shor Circuit'
        
        return circuit
        

    def estimate_phase(self, exponentiation_base, number, precision, task_log):
        
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
            
            power = 2**camod_index
            
            cme_circuit = self.controlled_modular_exponentiation(
                exponentiation_base, power, number, ancilla_qubits_count, task_log
            )
            
            circuit.append(cme_circuit, [camod_index] + [*ancilla_qubits])
        
        inverted_qft_circuit = build_qft_circuit(qubits_count=counting_qubits_count, 
                                                 inverted=True)
                                                 
        # task_log(f'SHOR inverted_qft_circuit: \n{inverted_qft_circuit}')
            
        circuit.append(inverted_qft_circuit, counting_qubits)
        
        circuit.measure(counting_qubits, measurement_bits)
                           
        task_log(f'SHOR circuit: \n{circuit}')
        
        return circuit
        
        
    def controlled_modular_exponentiation(self, exponentiation_base, power, number, ancilla_qubits_count, task_log):
        
        
        
        me_circuit = QuantumCircuit(ancilla_qubits_count)        
        
        for iteration in range(power):
            
            me_circuit.z(0)
            
        me_gate = me_circuit.to_gate()
        
        me_gate.name = f"{exponentiation_base}^{power} mod {number}"
        
        controlled_me_gate = me_gate.control()
        
        task_log(f'SHOR me_circuit:\n {me_circuit}')  
        task_log(f'SHOR me_gate:\n {me_gate}')  
        task_log(f'SHOR controlled_me_gate:\n {controlled_me_gate}')  
        
        return controlled_me_gate


run_values = {'number': '15', 'precision': '2', 'exponentiation_base': '7'}

Shor().shor(run_values, print)