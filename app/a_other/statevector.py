
from qiskit import Aer, ClassicalRegister, QuantumRegister, QuantumCircuit, execute
from qiskit.tools.monitor import job_monitor


ONE_STATE = 0, 1
ZERO_STATE = 1, 0
MINUS_STATE = 2**-0.5, -(2**-0.5)


test_circuit = QuantumCircuit(1)

test_circuit.initialize(ONE_STATE)

test_circuit.measure_all()


backend = Aer.get_backend('qasm_simulator')

test_circuit.save_statevector()

job = execute(test_circuit, backend=backend, shots=1024)

job_monitor(job, interval=5)

result = job.result()

statevector = result.get_statevector()

counts = result.get_counts()

print(f'SUDOKU statevector: {statevector}')

print(f'SUDOKU counts:')
[print(f'{state}: {count}') for state, count in sorted(counts.items())]