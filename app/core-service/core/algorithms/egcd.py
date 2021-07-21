def egcd(run_values):
    
    a, b = map(int, map(run_values.get, ('a', 'b')))

    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
        
    # print('A, B:', a, b)
    # print('GCD (Old remainder):', old_r)
    # print('Bézout coefficients (Old S, Old T):', old_s, old_t)
    # print()
    # print('Formula:')
    # print('a * x + b * y = d')
    # print(f'{a} * {old_s} + {b} * {old_t} = {old_r}')
    # print()
    
    return {'GCD': old_r,
            'Bézout coefficients': (old_s, old_t)}