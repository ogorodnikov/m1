# from math import gcd
# from random import randint

from math import log

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
        precision = 8
        
        phase = self.estimate_phase(exponentiation_base, precision)
    
        # circuit = QuantumCircuit(1, 1)
        # circuit.name = 'Shor Circuit'
        
        # return circuit
        

    def estimate_phase(self, exponentiation_base, precision):
        
        """ https://qiskit.org/textbook/ch-algorithms/shor.html """
        
        print(f'SHOR exponentiation_base: {exponentiation_base}')
        print(f'SHOR precision: {precision}')
        
        counting_qubits_count = precision
        
        counting_qubits = range(counting_qubits_count)
        
        print(f'SHOR counting_qubits: {counting_qubits}')
        
        ancilla_qubits_count = int(log(precision, 2)) + 1
        
        print(f'SHOR ancilla_qubits_count: {ancilla_qubits_count}')
        
        ancilla_qubits = range(counting_qubits_count, 
                               counting_qubits_count + ancilla_qubits_count)

        print(f'SHOR ancilla_qubits: {ancilla_qubits}')
        
        register_qubit = counting_qubits_count + ancilla_qubits_count - 1

        print(f'SHOR register_qubit: {register_qubit}')
        
                                       
        circuit = QuantumCircuit(counting_qubits_count + ancilla_qubits_count, 
                                 counting_qubits_count)
                                 
        for counting_qubit in counting_qubits:
            circuit.h(counting_qubit)
            
        circuit.name = ''
        
        circuit.x(register_qubit)
        
        # for ancilla_index in ancilla_qubits:
            
        #     circuit.append(self.controlled_amod15(exponentiation_base, 2**ancilla_index),
        #                   [ancilla_index] + [counting_qubits])
                           
        print(f'SHOR circuit: \n{circuit}')
        

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