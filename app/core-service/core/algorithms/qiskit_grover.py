from qiskit import *

from qiskit.circuit.library import Diagonal

from qiskit_textbook.problems import grover_problem_oracle




def initialize_s(qc, qubits):
    """Apply a H-gate to 'qubits' in qc"""
    for q in qubits:
        qc.h(q)
    return qc
    
    
def diffuser(nqubits):
    qc = QuantumCircuit(nqubits)
    # Apply transformation |s> -> |00..0> (H-gates)
    for qubit in range(nqubits):
        qc.h(qubit)
    # Apply transformation |00..0> -> |11..1> (X-gates)
    for qubit in range(nqubits):
        qc.x(qubit)
    # Do multi-controlled-Z gate
    qc.h(nqubits-1)
    qc.mct(list(range(nqubits-1)), nqubits-1)  # multi-controlled-toffoli
    qc.h(nqubits-1)
    # Apply transformation |11..1> -> |00..0>
    for qubit in range(nqubits):
        qc.x(qubit)
    # Apply transformation |00..0> -> |s>
    for qubit in range(nqubits):
        qc.h(qubit)
    # We will return the diffuser as a gate
    U_s = qc.to_gate()
    U_s.name = "U$_s$"
    return U_s

# n = 2
# grover_circuit = QuantumCircuit(n)

# grover_circuit = initialize_s(grover_circuit, [0,1])
# grover_circuit.cz(0,1)
# grover_circuit.barrier()

# grover_circuit.h([0,1])
# grover_circuit.z([0,1])
# grover_circuit.cz(0,1)
# grover_circuit.h([0,1])


# print(grover_circuit)


secret_index = 2

qubit_count = 2
elements_count = 2 ** qubit_count

diagonal_elements = [1] * elements_count
diagonal_elements[secret_index] = -1

print(diagonal_elements)
    
phase_oracle = Diagonal(diagonal_elements)

# phase_oracle = grover_problem_oracle(qubit_count, variant=10, print_solutions=True)

phase_oracle.name = 'Phase Oracle'

print(phase_oracle.decompose())
print(phase_oracle.decompose().decompose())
print(phase_oracle.decompose().decompose().decompose())

grover_circuit = QuantumCircuit(qubit_count)

grover_circuit = initialize_s(grover_circuit, range(qubit_count))

grover_circuit.append(phase_oracle, range(qubit_count))

# grover_circuit.cz(0, 2)
# grover_circuit.cz(1, 2)


grover_circuit.barrier()

for qubit in range(qubit_count):
    grover_circuit.h(qubit)

for qubit in range(qubit_count):
    grover_circuit.x(qubit)
    
for qubit in range(qubit_count-1):
    grover_circuit.i(qubit)

grover_circuit.h(qubit_count-1)
grover_circuit.mct(list(range(qubit_count-1)), qubit_count-1)
grover_circuit.h(qubit_count-1)

for qubit in range(qubit_count-1):
    grover_circuit.i(qubit)

for qubit in range(qubit_count):
    grover_circuit.x(qubit)

for qubit in range(qubit_count):
    grover_circuit.h(qubit)


print(grover_circuit)



backend = Aer.get_backend('qasm_simulator')

# state vector

sv_grover_circuit = grover_circuit.copy()
sv_grover_circuit.save_statevector()

sv_job = execute(sv_grover_circuit, backend=backend, shots=1000)

sv_result = sv_job.result()

state_vector = sv_result.get_statevector()

print('State vector:')

[print(f'{state}') for state in state_vector]


# counts

grover_circuit.measure_all()

job = execute(grover_circuit, backend=backend, shots=1000)

result = job.result()

counts = result.get_counts()

print('Counts:')

[print(f'{state}: {count}') for state, count in sorted(counts.items())]

