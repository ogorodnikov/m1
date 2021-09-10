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
        
    


def shor(run_values, task_log):
    
    number_input = run_values.get('number')
    number = int(number_input)
    
    random_pick = randint(0, number)
    
    factor = gcd(number, random_pick)
    
    if factor != 1:
        
        factors = factor, number // factor
    
    else:
        
        coprime = random_pick
        
        period = get_period_classical(number, coprime)
        
    
    
    task_log(f'SHOR number: {number}')
    task_log(f'SHOR coprime: {coprime}')
    task_log(f'SHOR period: {period}')