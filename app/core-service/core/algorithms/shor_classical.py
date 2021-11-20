from math import gcd
from random import randint


MAX_EXPONENTIAL_BASE_PICKS = 10


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