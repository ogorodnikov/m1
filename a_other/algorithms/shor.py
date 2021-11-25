    theoretical_qubits_count = 4 * math.ceil(math.log(number, 2)) + 2
    
    print(f'SHOR theoretical_qubits_count: {theoretical_qubits_count}')
    
    
    # phases = [sum(math.pi * digit * 2 ** (j - i) for j, digit in enumerate(digits[:i + 1]))
    #               for i, _ in enumerate(digits)]