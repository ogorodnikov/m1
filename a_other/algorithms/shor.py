    theoretical_qubits_count = 4 * math.ceil(math.log(number, 2)) + 2
    
    print(f'SHOR theoretical_qubits_count: {theoretical_qubits_count}')
    
    
    # phases = [sum(math.pi * digit * 2 ** (j - i) for j, digit in enumerate(digits[:i + 1]))
    #               for i, _ in enumerate(digits)]
    
    
    
    ###   Plot   ###
    
    from qiskit.visualization import circuit_drawer
        
    # figure = modexp_circuit.draw(output='mpl')
    
    # print(f"SHOR figure: {figure}")
    
    # style = {'figwidth': 10}
    
    circuit_figure_path = "/home/ec2-user/environment/m1/app/core-service/core/static/circuits/modexp.png"
    
    # circuit_drawer(modexp_circuit.decompose(), output='mpl', scale=0.5, filename=circuit_figure_path)
    
    modexp_circuit.decompose().draw(output='mpl', scale=0.5, filename=circuit_figure_path)
    
    # figure.savefig(circuit_figure_path, bbox_inches='tight', style=style)
    
    
    
    
    ###   modexp   ###
    
    # partial_base = pow(base, 2**i, number)