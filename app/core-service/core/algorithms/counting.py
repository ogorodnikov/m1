from qiskit import QuantumCircuit

try:
    from grover import build_diffuser
except ModuleNotFoundError:
    from core.algorithms.grover import build_diffuser

try:
    from qft import create_qft_circuit
except ModuleNotFoundError:
    from core.algorithms.qft import create_qft_circuit
    

def counting(run_values, task_log):
    
    task_log(f'COUNT run_values: {run_values}')