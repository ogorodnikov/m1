from math import gcd
from random import randint

from qiskit import QuantumCircuit, Aer

from core.algorithms.qft import build_qft_circuit


def get_period_classical(modulo, x):
    
    period = 1
    modular_exponent = x
    
    while modular_exponent != 1:
        
        modular_exponent = (modular_exponent * x) % modulo
        period += 1
        
    return period


def shor_classical(run_values, task_log):
    
    number_input = run_values.get('number')
    number = int(number_input)
    
    period = None
    coprime = None
    
    random_pick = randint(0, number)
    
    factor = gcd(number, random_pick)
    
    if factor != 1:
        
        factor_p = factor

    else:
        
        coprime = random_pick
        
        period = get_period_classical(number, coprime)
        
        if period % 2:
            
            ValueError("Period is odd")
            
        factor_p = gcd(random_pick ** (period // 2) + 1, number)
        
    
    factor_q = number // factor_p
    
    
    task_log(f'SHOR number: {number}')
    task_log(f'SHOR random_pick: {random_pick}')
    task_log(f'SHOR coprime: {coprime}')
    task_log(f'SHOR period: {period}')
    
    task_log(f'SHOR factor_p: {factor_p}')
    task_log(f'SHOR factor_q: {factor_q}')
    
    return factor_p, factor_q
    
    
def shor(run_values, task_log):
    
    shor_classical(run_values, task_log)
    
    task_log(f'SHOR Test 2')
    
    circuit = QuantumCircuit(1, 1)
    circuit.name = 'Shor Circuit'
    
    return circuit