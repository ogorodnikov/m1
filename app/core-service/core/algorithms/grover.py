from qiskit import *
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import backend_overview, job_monitor


def grover(run_values):
    
    qubit_count = 3
    
    circuit = QuantumCircuit(qubit_count)
    
    for qubit in range(qubit_count):
        circuit.h(qubit)

    circuit.cz(0, qubit_count - 1)
    circuit.cz(1, qubit_count - 1)
    
    circuit.barrier()
    
    for qubit in range(qubit_count):
        circuit.h(qubit)

    for qubit in range(qubit_count):
        circuit.x(qubit)
        
    for qubit in range(qubit_count-1):
        circuit.i(qubit)

    circuit.h(qubit_count-1)
    circuit.mct(list(range(qubit_count-1)), qubit_count-1)
    circuit.h(qubit_count-1)
    
    for qubit in range(qubit_count-1):
        circuit.i(qubit)

    for qubit in range(qubit_count):
        circuit.x(qubit)

    for qubit in range(qubit_count):
        circuit.h(qubit)
    
    circuit.measure_all()
    
    print(circuit)
    
    
    # run
    
    backend = Aer.get_backend('qasm_simulator')
    
    job = execute(circuit, backend=backend, shots=1000)
    
    result = job.result()
    
    counts = result.get_counts()

    return counts
    
print(grover('11'))