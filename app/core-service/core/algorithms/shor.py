# from math import gcd
# from random import randint

from qiskit import Aer
from qiskit import QuantumCircuit

# from core.algorithms.qft import build_qft_circuit
from qft import build_qft_circuit


# MAX_EXPONENTIAL_BASE_PICKS = 10


class Shor:
    
    def shor(self, run_values):
        
        print(f'>>> SHOR')    
        
        number_input = run_values.get('number')
        number = int(number_input)
        
        print(f'SHOR number: {number}')
        
        exponentiation_base = 7
        
        print(f'SHOR exponentiation_base: {exponentiation_base}')
        
        # self.exponent_by_squaring(2, 1000000)
        
        print(2**1000000)
        
        # phase = self.estimate_phase(a)
    
        # circuit = QuantumCircuit(1, 1)
        # circuit.name = 'Shor Circuit'
        
        # return circuit
        
    def exponent_by_squaring(self, exponentiation_base, power):
        
        power_binary = list(map(int, bin(power)[2:]))

        print(f'exponentiation_base: {exponentiation_base}')
        print(f'power: {power}')
        print(f'power_binary: {power_binary}')
        
        result = 1
        
        for power_bit in power_binary:
            
            result **= 2
            result *= exponentiation_base ** power_bit
            
            print(f'SHOR power_bit: {power_bit}')
            print(f'SHOR result: {result}')
        
        return result
        

    def estimate_phase(self, exponentiation_base):
        
        """ https://qiskit.org/textbook/ch-algorithms/shor.html """
        
        counting_qubits_count = 8
        
        counting_qubits = range(counting_qubits_count)
        
        ancilla_qubits_count = 4
        
        ancilla_qubits = range(counting_qubits_count, 
                               counting_qubits_count + ancilla_qubits_count)
                             
        register_qubit = range(counting_qubits_count + ancilla_qubits_count,
                               counting_qubits_count + ancilla_qubits_count + 1)
                               
        circuit = QuantumCircuit(counting_qubits_count + ancilla_qubits_count, 
                                 counting_qubits_count)
        
        for counting_qubit in counting_qubits:
            circuit.h(counting_qubit)
            
        circuti.name = ''
        
        circuit.x(register_qubit)
        
        for ancilla_index in ancilla_qubits:
            
            circuit.append(self.controlled_amod15(exponentiation_base, 2**ancilla_index),
                           [ancilla_index] + [counting_qubits])
                           
        print(f'SHOR circuit: {circuit}')
        

    def controlled_amod15(self, exponentiation_base, power):
        
        camod_circuit = QuantumCircuit(4)        
        
        for iteration in range(power):
            
            if exponentiation_base in [2,13]:
                camod_circuit.swap(0,1)
                camod_circuit.swap(1,2)
                camod_circuit.swap(2,3)
                
            elif exponentiation_base in [7,8]:
                camod_circuit.swap(2,3)
                camod_circuit.swap(1,2)
                camod_circuit.swap(0,1)
                
            elif exponentiation_base == 11:
                camod_circuit.swap(1,3)
                camod_circuit.swap(0,2)
                
            if exponentiation_base in [7,11,13]:
                for q in range(4):
                    circuit.x(q)
                    
        camod_gate = camod_circuit.to_gate()
        
        camod_gate.name = f"{exponentiation_base} ** {power} mod 15"
        
        controlled_camod_gate = camod_gate.control()
        
        print(f'SHOR camod_circuit: {camod_circuit}')  
        print(f'SHOR camod_gate: {camod_gate}')  
        print(f'SHOR controlled_camod_gate: {controlled_camod_gate}')  
        
        return controlled_camod_gate



run_values = {'number': '330023'}

Shor().shor(run_values)