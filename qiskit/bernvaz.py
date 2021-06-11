from qiskit import *

import matplotlib.pyplot as plt

from qiskit.tools.visualization import plot_histogram



print("Hello BernVaz")

secret_number = '101001'

circuit = QuantumCircuit(7, 6)

circuit.x(6)
circuit.h(range(7))

circuit.barrier()

for i, digit in reversed(tuple(enumerate(reversed(secret_number)))):
    if digit == '1':
        circuit.cx(i, 6)
        
circuit.barrier()
        
circuit.h(range(6))

circuit.measure(range(6), range(6))

# circuit.draw(output='mpl')

# circuit.draw()

print(circuit)
