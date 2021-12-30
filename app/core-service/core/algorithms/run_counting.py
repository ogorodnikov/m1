from qiskit import Aer
from qiskit import execute

from counting import quantum_counting, quantum_counting_post_processing


# run_values = {'secret_1': '10111', 'secret_2': '10101'}

run_values = {'precision': '4', 'secret_1': '1011', 'secret_2': '1010'}

# run_values = {'secret_1': '1011', 'secret_2': '1010', 'secret_3': '0111', 'secret_4': '0101'}

circuit = quantum_counting(run_values=run_values, task_log=print)

backend = Aer.get_backend('aer_simulator')

job = execute(circuit, backend, shots=1024)

counts = job.result().get_counts()


run_data = {'Result': {'Counts': counts}, 'Run Values': run_values}
            
            
quantum_counting_post_processing(run_data=run_data, task_log=print)


# run_data = {'Result': {'Counts': counts}, 
            # 'Run Values': {'number': number, 'base': base}}

# shor.shor_post_processing(run_data=run_data, task_log=print)