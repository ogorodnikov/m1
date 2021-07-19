from qiskit import *
from core import app

# from matplotlib import pyplot as plt
# from qiskit.tools.visualization import plot_histogram


def bernvaz(run_values):
    
    secret = run_values.get('secret')

    HIDDEN_DIGITS = str(secret)
    
    hidden_len = len(HIDDEN_DIGITS)
    
    input_qubit_indices = range(hidden_len)
    measure_bits_indices = input_qubit_indices
    
    output_qubit_index = hidden_len
    
    all_qubit_indices = range(hidden_len + 1)
    
    
    circuit = QuantumCircuit(hidden_len + 1, hidden_len)
    
    circuit.x(output_qubit_index)
    circuit.h(all_qubit_indices)
    
    circuit.barrier()
    
    for input_qubit_index, digit in enumerate(reversed(HIDDEN_DIGITS)):
        if digit == '1':
            circuit.cx(input_qubit_index, output_qubit_index)
            
    circuit.barrier()
            
    circuit.h(input_qubit_indices)
    
    circuit.measure(input_qubit_indices, measure_bits_indices)
    
    # circuit.draw(output='mpl')
    # circuit.draw()
    
    simulator = Aer.get_backend('qasm_simulator')
    result = execute(circuit, backend=simulator, shots=1).result()
    
    counts = result.get_counts()
    
    app.logger.info(f"BERVAZ run_values: {run_values}")
    app.logger.info(f"BERVAZ secret: {secret}")
    app.logger.info(f"BERVAZ circuit: \n\n{circuit}\n")
    app.logger.info(f"BERVAZ counts: {counts}")
    
    return {'Counts:': counts}