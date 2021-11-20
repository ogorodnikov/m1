from math import gcd
from random import randint

from qiskit import Aer
from qiskit import QuantumCircuit

# from core.algorithms.qft import build_qft_circuit
from qft import build_qft_circuit


MAX_EXPONENTIAL_BASE_PICKS = 10



def controlled_amod15(a, power):
    
    # Controlled multipliaction by a mod 15 
    # for a in 2, 7, 8, 11, 13
    
    camod_circuit = QuantumCircuit(4)        
    
    for iteration in range(power):
        
        if a in [2,13]:
            camod_circuit.swap(0,1)
            camod_circuit.swap(1,2)
            camod_circuit.swap(2,3)
            
        elif a in [7,8]:
            camod_circuit.swap(2,3)
            camod_circuit.swap(1,2)
            camod_circuit.swap(0,1)
            
        elif a == 11:
            camod_circuit.swap(1,3)
            camod_circuit.swap(0,2)
            
        if a in [7,11,13]:
            for q in range(4):
                circuit.x(q)
                
    camod_gate = camod_circuit.to_gate()
    
    camod_gate.name = f"{a} ** {power} mod 15"
    
    controlled_camod_gate = camod_gate.control()
    
    task_log(f'SHOR camod_circuit: {camod_circuit}')  
    task_log(f'SHOR camod_gate: {camod_gate}')  
    task_log(f'SHOR controlled_camod_gate: {controlled_camod_gate}')  
    
    return controlled_camod_gate
    

def qpe_a_mod15(a):
    
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
    
    circuit.x(register_qubit)
    
    for ancilla_index in ancilla_qubits:
        
        circuit.append(controlled_amod15(a, 2**ancilla_index),
                       [ancilla_index] + [counting_qubits])
                       
    task_log(f'SHOR circuit: {circuit}')


def shor(run_values, task_log):
    
    task_log(f'>>> SHOR')    
    
    number_input = run_values.get('number')
    number = int(number_input)
    
    task_log(f'SHOR number: {number}')
    
    a = 7
    
    task_log(f'SHOR a: {a}')
    
    
    task_log(f'>>> SHOR phase')
    
    phase = qpe_a_mod15(a)
    
    task_log(f'>>> SHOR after phase')        

    circuit = QuantumCircuit(1, 1)
    circuit.name = 'Shor Circuit'
    
    return circuit


run_values = {'number': '330023'}
    
shor(run_values, print)
        
        

     
     
     
    



###   Shor classical   ###
    
    
def shor_classical(run_values, task_log):
    
    number_input = run_values.get('number')
    number = int(number_input)
    
    task_log(f'SHOR number: {number}')
    
    factor = None
    
    retry_index = 0
    
    while not factor or retry_index > MAX_EXPONENTIAL_BASE_PICKS:
        
        factor = get_factor_classical(number, task_log)
        
        retry_index += 1
        
    if not factor:
        
        task_log(f'SHOR factor not found during {MAX_EXPONENTIAL_BASE_PICKS} tries')         
        
        return
        
    
    factor_p, factor_q = factor, number // factor
    
    task_log(f'SHOR factor_p: {factor_p}')   
    task_log(f'SHOR factor_q: {factor_q}')
    
    return factor_p, factor_q
    
    
        
        
def get_factor_classical(number, task_log):
    
    exponentiation_base = randint(0, number)
    
    task_log(f'SHOR exponentiation_base: {exponentiation_base}')
    
    factor = gcd(number, exponentiation_base)
    
    task_log(f'SHOR factor: {factor}')    
    
    if factor == 1:
        
        period = get_period_classical(number, exponentiation_base, task_log)

        task_log(f'SHOR period: {period}')
        
        if period % 2:
            
            task_log(f'SHOR period is odd')
            
            return
            
        factor = gcd(exponentiation_base ** (period // 2) + 1, number)
        
    return factor


def get_period_classical(number, exponentiation_base, task_log):
    
    task_log(f'SHOR get_period_classical: {number, exponentiation_base}')
    
    period = 1
    
    modulo = number
    modular_exponent = exponentiation_base
    
    task_log(f'SHOR modulo: {modulo}')
    task_log(f'SHOR initial period: {period}')    
    task_log(f'SHOR initial modular_exponent: {modular_exponent}')    
    
    while modular_exponent != 1:
        
        modular_exponent = (modular_exponent * exponentiation_base) % modulo
        period += 1
        
        if period % 10000000 == 0:
        
            task_log(f'SHOR modular_exponent: {modular_exponent}') 
            task_log(f'SHOR period: {period}') 
        
    return period
    
    
