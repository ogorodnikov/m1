from qiskit import *

from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import backend_overview, job_monitor

from qiskit.circuit.library import Diagonal


def build_phase_oracle(secrets, elements_count):
    
    diagonal_elements = [1] * elements_count
    
    for secret in secrets:
        secret_string = ''.join('1' if letter == '1' else '0' for letter in secret)
        secret_index = int(secret_string, 2)
        diagonal_elements[secret_index] = -1

    phase_oracle = Diagonal(diagonal_elements)
    phase_oracle.name = 'Phase Oracle'
    
    return phase_oracle
    
    
def build_diffuser(qubit_count):
    
    diffuser_circuit = QuantumCircuit(qubit_count)
        
    for qubit in range(qubit_count):
        diffuser_circuit.h(qubit)

    for qubit in range(qubit_count):
        diffuser_circuit.x(qubit)
        
    for qubit in range(1, qubit_count):
        diffuser_circuit.i(qubit)

    diffuser_circuit.h(0)
    diffuser_circuit.mct(list(range(1, qubit_count)), 0)
    diffuser_circuit.h(0)
    
    for qubit in range(1, qubit_count):
        diffuser_circuit.i(qubit)

    for qubit in range(qubit_count):
        diffuser_circuit.x(qubit)

    for qubit in range(qubit_count):
        diffuser_circuit.h(qubit)
        
    diffuser_circuit.name = 'Diffuser'
    
    return diffuser_circuit
    
    
def get_least_busy_backend(provider, total_qubit_count):
    
    # backend_overview()
    
    backend_filter = lambda backend: (not backend.configuration().simulator 
                                      and backend.configuration().n_qubits >= total_qubit_count
                                      and backend.status().operational==True)
        
    least_busy_backend = least_busy(provider.backends(filters=backend_filter))
    
    return least_busy_backend
    

def grover(run_values):
    
    # run_mode = 'simulator'
    run_mode = 'quantum_device'
    run_values = {'secret': ('1111',),}
    
    secrets = run_values.get('secret')
    secret_count = len(secrets)
    
    qubit_count = len(max(secrets, key=len))
    qubits = range(qubit_count)

    elements_count = 2 ** qubit_count
    
    repetitions =  (elements_count / secret_count) ** 0.5 * 3.14 / 4
    repetitions_count = int(repetitions)
    
    phase_oracle = build_phase_oracle(secrets, elements_count)
    
    diffuser = build_diffuser(qubit_count)

    circuit = QuantumCircuit(qubit_count)
    
    for qubit in qubits:
        circuit.h(qubit)

    for i in range(repetitions_count):
    
        circuit.barrier()
        circuit.append(phase_oracle, qubits)
        circuit.append(diffuser, qubits)
        
    circuit.measure_all()
    
    print(f'GROVER secrets: {secrets}')
    print(f'GROVER secret_count: {secret_count}')
    print(f'GROVER qubit_count: {qubit_count}')
    print(f'GROVER elements_count: {elements_count}')
    
    print(f'GROVER repetitions: {repetitions}')
    print(f'GROVER repetitions_count: {repetitions_count}')

    print(f'GROVER phase_oracle: \n\n{phase_oracle}')
    print(f'GROVER phase_oracle 1 decomposition:')
    print(phase_oracle.decompose())
    print(f'GROVER phase_oracle 2 decomposition:')
    print(phase_oracle.decompose().decompose())
    print(f'GROVER phase_oracle 3 decomposition:')
    print(phase_oracle.decompose().decompose().decompose())

    print(f'GROVER diffuser: \n{diffuser}')
    
    print(f"GROVER circuit: \n{circuit}")
    

    ###   Run   ###

    if run_mode == 'simulator':
        
        backend = Aer.get_backend('qasm_simulator')
        
        
    if run_mode == 'quantum_device':
    
        # qiskit_token = app.config.get('QISKIT_TOKEN')
        qiskit_token = xxx
        IBMQ.save_account(qiskit_token)
        
        if not IBMQ.active_account():
            IBMQ.load_account()
            
        provider = IBMQ.get_provider()
        
        print(f"GROVER provider: {provider}")
        print(f"GROVER provider.backends(): {provider.backends()}")
        
        # backend = provider.get_backend('ibmq_manila')

        backend = get_least_busy_backend(provider, qubit_count)
        

    print(f"GROVER run_mode: {run_mode}")
    print(f"GROVER backend: {backend}")


    job = execute(circuit, backend=backend, shots=1024)
    
    job_monitor(job, interval=5)
    
    result = job.result()
    
    counts = result.get_counts()
    
    print(f"GROVER counts:")
    [print(f'{state}: {count}') for state, count in sorted(counts.items())]

    return {'Counts:': counts}
    
    
result = grover('bonya')
