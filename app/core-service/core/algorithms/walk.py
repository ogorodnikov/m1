from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister


def walk(run_values, task_log):
    
    # Logs
    
    task_log(f'WALK run_values: {run_values}')