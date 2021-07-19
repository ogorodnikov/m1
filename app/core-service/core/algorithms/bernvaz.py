# from qiskit import QuantumCircuit, Aer

from qiskit import *
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import backend_overview, job_monitor

from core import app

# from matplotlib import pyplot as plt
# from qiskit.tools.visualization import plot_histogram


def bernvaz(run_values):
    
    secret = run_values.get('secret')
    run_mode = run_values.get('run_mode', 'simulator')

    HIDDEN_DIGITS = str(secret)
    
    hidden_qubit_count = len(HIDDEN_DIGITS)
    total_qubit_count = hidden_qubit_count + 1
    
    input_qubit_indices = range(hidden_qubit_count)
    measure_bits_indices = input_qubit_indices
    
    output_qubit_index = hidden_qubit_count
    
    all_qubit_indices = range(total_qubit_count)
    
    
    circuit = QuantumCircuit(total_qubit_count, hidden_qubit_count)
    
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
    
    
    ###   Run   ###
    
    if run_mode == 'simulator':
        
        # backend = provider.get_backend('ibmq_qasm_simulator')
        
        backend = Aer.get_backend('qasm_simulator')
        
    if run_mode == 'quantum_device':
    
        qiskit_token = app.config.get('QISKIT_TOKEN')
        
        IBMQ.save_account(qiskit_token)
        provider = IBMQ.load_account()

        # backend = get_least_busy_backend(total_qubit_count)
        
        backend = provider.get_backend('ibmq_manila')

        app.logger.info(f"BERVAZ provider: {provider}")
        app.logger.info(f"BERVAZ provider.backends(): {provider.backends()}")
        app.logger.info(f"BERVAZ backend: {backend}")
        

    job = execute(circuit, backend=backend, shots=1)
    
    job_monitor(job, interval=5)
    
    result = job.result()
    
    counts = result.get_counts()
    
    app.logger.info(f"BERVAZ run_values: {run_values}")
    app.logger.info(f"BERVAZ run_mode: {run_mode}")
    app.logger.info(f"BERVAZ secret: {secret}")
    app.logger.info(f"BERVAZ circuit: \n\n{circuit}\n")
    app.logger.info(f"BERVAZ counts: {counts}")
    
    return {'Counts:': counts}
    

def get_least_busy_backend(total_qubit_count):
    
    # backend_overview()
    
    backend_filter = lambda backend: (not backend.configuration().simulator 
                                      and backend.configuration().n_qubits >= total_qubit_count
                                      and backend.status().operational==True)
        
    least_busy_backend = least_busy(provider.backends(filters=backend_filter))
    
    return least_busy_backend