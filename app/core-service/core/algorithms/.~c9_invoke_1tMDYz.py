import math
import numpy as np
from qiskit import Aer
from qiskit.utils import QuantumInstance
from qiskit.algorithms import Shor


"""   https://github.com/Qiskit/qiskit-tutorials/blob/0994a317891cf688f55ebed5a06f8a227c8440ac/tutorials/algorithms/08_factorizers.ipynb   """
"""   https://github.com/Qiskit/qiskit-terra/blob/main/qiskit/algorithms/factorizers/shor.py   """


number = 15

backend = Aer.get_backend('aer_simulator')

quantum_instance = QuantumInstance(backend, shots=1024)

shor = Shor(quantum_instance=quantum_instance)

result = shor.factor(number)

print(f"Result factors: {result.factors[0]}")

theoretical_qubits_count = 4 * math.ceil(math.log(number, 2)) + 2
actual_qubits_count = shor.construct_circuit(number).num_qubits

print(f'SHOR theoretical_qubits_count {theoretical_qubits_count}')
print(f'SHOR Actual number of qubits of circuit: {}')