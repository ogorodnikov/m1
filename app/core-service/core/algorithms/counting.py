from qiskit import QuantumCircuit

try:
    from grover import build_phase_oracle
    from grover import build_diffuser
except ModuleNotFoundError:
    from core.algorithms.grover import build_phase_oracle
    from core.algorithms.grover import build_diffuser

try:
    from qft import create_qft_circuit
except ModuleNotFoundError:
    from core.algorithms.qft import create_qft_circuit
    
    
def example_grover_iteration(qubits_count, secrets):

    circuit = QuantumCircuit(4)
    
    # Oracle
    circuit.h([2,3])
    circuit.ccx(0,1,2)
    circuit.h(2)
    circuit.x(2)
    circuit.ccx(0,2,3)
    circuit.x(2)
    circuit.h(3)
    circuit.x([1,3])
    circuit.h(2)
    circuit.mct([0,1,3],2)
    circuit.x([1,3])
    circuit.h(2)
    
    circuit.barrier()
    
    # Diffuser
    circuit.h(range(3))
    circuit.x(range(3))
    circuit.z(3)
    circuit.mct([0,1,2],3)
    circuit.x(range(3))
    circuit.h(range(3))
    circuit.z(3)
    
    return circuit
    

def quantum_counting(run_values, task_log):
    
    secrets = [value for key, value in run_values.items() if 'secret' in key]
    secret_count = len(secrets)
    
    qubits_count = len(max(secrets, key=len))
    
    grover_iteration_circuit = example_grover_iteration(qubits_count, secrets)
    
    task_log(f'COUNT run_values: {run_values}')
    task_log(f'COUNT grover_iteration_circuit:\n{grover_iteration_circuit}')
    