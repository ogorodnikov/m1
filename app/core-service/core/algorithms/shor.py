from math import gcd
from random import randint

from qiskit import QuantumCircuit, Aer

from core.algorithms.qft import build_qft_circuit


MAX_EXPONENTIAL_BASE_PICKS = 10


def shor(run_values, task_log):
    
    shor_classical(run_values, task_log)

    circuit = QuantumCircuit(1, 1)
    circuit.name = 'Shor Circuit'
    
    return circuit
    
    
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
        
        period = get_period_classical(number, exponentiation_base)

        task_log(f'SHOR period: {period}')
        
        if period % 2:
            
            task_log(f'SHOR period is odd')
            
            return
            
        factor = gcd(exponentiation_base ** (period // 2) + 1, number)
        
    return factor


def get_period_classical(number, exponentiation_base):
    
    period = 1
    
    modulo = number
    modular_exponent = exponentiation_base
    
    while modular_exponent != 1:
        
        modular_exponent = (modular_exponent * exponentiation_base) % modulo
        period += 1
        
    return period
    
    
