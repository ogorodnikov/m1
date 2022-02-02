import sys 

sys.path.append('/home/ec2-user/environment/m1/app/core-service/core/algorithms')

from qiskit import Aer
from qiskit import execute

from iqae import iqae


RUN_VALUES = {'bernoulli_probability': '0.6', 
              'precision': '5'}


# Circuit

circuit = iqae(run_values=RUN_VALUES, task_log=print)


# # Run

# backend = Aer.get_backend('aer_simulator')

# job = execute(circuit, backend, shots=1024)

# counts = job.result().get_counts()


# # Post-processing

# RUN_DATA = {'Result': {'Counts': counts}, 
#             'Run Values': RUN_VALUES}

# iqae_post_processing(run_data=RUN_DATA, task_log=print)