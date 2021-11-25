def calculate_egcd(a, b):
    
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
        
    greatest_common_divisor = old_r
    bezout_s = old_s
    bezout_t = old_t
        
    return greatest_common_divisor, bezout_s, bezout_t


def egcd(run_values, task_log):
    
    a = int(run_values['a'])
    b = int(run_values['b'])

    greatest_common_divisor, bezout_s, bezout_t = calculate_egcd(a, b)

    task_log(f'EGCD Formula:')
    task_log(f'EGCD a * x + b * y = d')
    task_log(f'EGCD {a} * {bezout_s} + {b} * {bezout_t} = {greatest_common_divisor}')
    
    task_log(f'EGCD a: {a}')
    task_log(f'EGCD b: {b}')
    task_log(f'EGCD greatest_common_divisor: {greatest_common_divisor}')
    task_log(f'EGCD bezout_s: {bezout_s}')
    task_log(f'EGCD bezout_t: {bezout_t}')
    
    return {'GCD': greatest_common_divisor, 
            'Bézout coefficients': (bezout_s, bezout_t)}