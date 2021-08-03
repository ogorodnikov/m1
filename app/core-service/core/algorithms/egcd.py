def egcd(run_values, task_log):
    
    a, b = map(int, map(run_values.get, ('a', 'b')))

    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
        
    task_log(f'A, B: {a}, {b}')
    task_log(f'GCD (Old remainder): {old_r}')
    task_log(f'Bézout coefficients (Old S, Old T): {old_s}, {old_t}')
    task_log(f'')
    task_log(f'Formula:')
    task_log(f'a * x + b * y = d')
    task_log(f'{a} * {old_s} + {b} * {old_t} = {old_r}')
    task_log(f'')
    
    return {'GCD': old_r,
            'Bézout coefficients': (old_s, old_t)}