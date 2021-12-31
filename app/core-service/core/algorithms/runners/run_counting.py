import sys 

sys.path.append('/home/ec2-user/environment/m1/app/core-service/core/algorithms')


from qiskit import Aer
from qiskit import execute

from counting import counting, counting_post_processing


# run_values = {'secret_1': '10111', 'secret_2': '10101'}

run_values = {'precision': '4', 'secret_1': '1011', 'secret_2': '1010'}

# run_values = {'precision': '2', 'secret_1': '10', 'secret_2': '11'}

# run_values = {'precision': '3', 'secret_1': '101', 'secret_2': '110'}

# run_values = {'secret_1': '1011', 'secret_2': '1010', 'secret_3': '0111', 'secret_4': '0101'}

circuit = counting(run_values=run_values, task_log=print)

backend = Aer.get_backend('aer_simulator')

job = execute(circuit, backend, shots=1024)

counts = job.result().get_counts()


run_data = {'Result': {'Counts': counts}, 'Run Values': run_values}
            
            
counting_post_processing(run_data=run_data, task_log=print)


# run_data = {'Result': {'Counts': counts}, 
            # 'Run Values': {'number': number, 'base': base}}

# shor.shor_post_processing(run_data=run_data, task_log=print)