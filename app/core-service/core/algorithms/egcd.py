# from core.runner import log


def egcd(run_values, log):
    
    task_id = run_values.get('task_id')
    
    a, b = map(int, map(run_values.get, ('a', 'b')))

    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
        
    log(f'A, B: {a}, {b}')
    log(f'GCD (Old remainder): {old_r}')
    log(f'Bézout coefficients (Old S, Old T): {old_s}, {old_t}')
    log(f'')
    log(f'Formula:')
    log(f'a * x + b * y = d')
    log(f'{a} * {old_s} + {b} * {old_t} = {old_r}')
    log(f'')
    
    return {'GCD': old_r,
            'Bézout coefficients': (old_s, old_t)}