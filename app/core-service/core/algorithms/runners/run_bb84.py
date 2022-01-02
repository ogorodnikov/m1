import sys 

sys.path.append('/home/ec2-user/environment/m1/app/core-service/core/algorithms')


from qiskit import Aer
from qiskit import execute

from bb84 import bb84, bb84_post_processing


# run_values = {'alice_bits': '10101011',
#               'alice_bases': 'XXXZXXXX',
#               'eve_bases': 'XZZZXZXX',
#               'bob_bases': 'XXXZZZXX',
#               'sample_indices': '0, 2, 3, 4'}

run_values = {'alice_bits': '101010',
              'alice_bases': 'XXXZXX',
              'eve_bases': 'XZZZXZ',
              'bob_bases': 'XXXZZZ',
              'sample_indices': '0, 2'}


circuit = bb84(run_values=run_values, task_log=print)


backend = Aer.get_backend('aer_simulator')

job = execute(circuit, backend, shots=1024)

counts = job.result().get_counts()


run_data = {'Result': {'Counts': counts}, 
            'Run Values': run_values}

bb84_post_processing(run_data=run_data, task_log=print)