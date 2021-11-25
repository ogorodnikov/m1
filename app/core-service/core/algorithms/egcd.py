def calculate_egcd(a, b):
    
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
        
    return old_r, old_s, old_t


def egcd(run_values, task_log):
    
    a = int(run_values['a'])
    b = int(run_values['b'])

    old_r, old_s, old_t = calculate_egcd(a, b)

    task_log(f'EGCD Formula:')
    task_log(f'EGCD a * x + b * y = d')
    task_log(f'EGCD {a} * {old_s} + {b} * {old_t} = {old_r}')
    
    task_log(f'EGCD a: {a}')
    task_log(f'EGCD b: {b}')
    task_log(f'EGCD GCD (Old remainder): {old_r}')
    task_log(f'EGCD Bézout coefficients (Old S, Old T): {old_s}, {old_t}')
    
    return {'GCD': old_r, 'Bézout coefficients': (old_s, old_t)}