from math import gcd
from math import log

from fractions import Fraction

from qiskit import QuantumCircuit

from core.algorithms.qft import create_qft_circuit


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
        
        circuit = self.estimate_phase(exponentiation_base, precision, task_log)
        circuit.name = 'Shor Circuit'
        
        return circuit
        

    def estimate_phase(self, exponentiation_base, precision, task_log):
        
        """ https://qiskit.org/textbook/ch-algorithms/shor.html """
        
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
        
        inverted_qft_circuit = create_qft_circuit(qubits_count=counting_qubits_count, 
                                                  inverted=True)
                                                 
        # task_log(f'SHOR inverted_qft_circuit: \n{inverted_qft_circuit}')
            
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


def shor(run_values, task_log):
    
    return Shor().shor(run_values, task_log)
    
    
def shor_post_processing(run_data, task_log):

    run_result = run_data.get('Result')
    run_values = run_data.get('Run Values')
    
    counts = run_result.get('Counts')
    
    number_str = run_values.get('number')
    exponentiation_base_str = run_values.get('exponentiation_base')
    
    number = int(number_str)
    exponentiation_base = int(exponentiation_base_str)
    
    sorted_counts = dict(sorted(counts.items(), key=lambda item: -item[1]))
  
    top_states = list(sorted_counts.keys())
    
    precision = len(top_states[0])
    

    task_log(f'SHOR run_data: {run_data}')
    task_log(f'SHOR run_result: {run_result}')
    task_log(f'SHOR run_values: {run_values}')

    task_log(f'SHOR number: {number}')
    task_log(f'SHOR exponentiation_base: {exponentiation_base}')
    
    task_log(f'SHOR counts: {counts}')
    task_log(f'SHOR sorted_counts: {sorted_counts}')
    task_log(f'SHOR top_states: {top_states}')
    task_log(f'SHOR precision: {precision}')
    
    orders = []
    
    for state in top_states:
        
        state_binary = int(state[::-1], 2)
        
        phase = state_binary / 2 ** precision
        
        phase_fraction = Fraction(phase).limit_denominator(15)
        
        order = phase_fraction.denominator
        
        orders.append(order)
        
        task_log(f'SHOR state: {state}')
        task_log(f'SHOR state_binary: {state_binary}')
        task_log(f'SHOR phase: {phase}')
        task_log(f'SHOR phase_fraction: {phase_fraction}')
        task_log(f'SHOR order: {order}')
    
    task_log(f'SHOR orders: {orders}')
    
    filtered_orders = list(filter(lambda order: order % 2 == 0, orders))

    task_log(f'SHOR filtered_orders: {filtered_orders}')
    
    factors = set()
    
    for order in filtered_orders:
        
        factor_p_1 = gcd(exponentiation_base ** (order // 2) - 1, number)
        factor_p_2 = gcd(exponentiation_base ** (order // 2) + 1, number)
        
        factor_q_1 = number // factor_p_1
        factor_q_2 = number // factor_p_2
        
        task_log(f'SHOR factor_p_1: {factor_p_1}')
        task_log(f'SHOR factor_p_2: {factor_p_2}')
        
        task_log(f'SHOR factor_q_1: {factor_q_1}')
        task_log(f'SHOR factor_q_2: {factor_q_2}')
        
        factors.add(factor_p_1)
        factors.add(factor_p_2)
        factors.add(factor_q_1)
        factors.add(factor_q_2)

    task_log(f'SHOR factors: {factors}')
    
    non_trivial_factors = list(factors - {1, number})

    task_log(f'SHOR non_trivial_factors: {non_trivial_factors}')
    
    return {'Factors': non_trivial_factors}