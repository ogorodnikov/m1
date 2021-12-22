from qiskit import Aer
from qiskit import execute

from counting import quantum_counting


run_values = {'secret_1': '10111', 'secret_2': '10101'}

circuit = quantum_counting(run_values=run_values, task_log=print)

# backend = Aer.get_backend('aer_simulator')

# job = execute(circuit, backend, shots=1024)

# counts = job.result().get_counts()        

# run_data = {'Result': {'Counts': counts}, 
            # 'Run Values': {'number': number, 'base': base}}

# shor.shor_post_processing(run_data=run_data, task_log=print)