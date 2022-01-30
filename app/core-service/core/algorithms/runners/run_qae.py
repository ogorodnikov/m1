import sys 

sys.path.append('/home/ec2-user/environment/m1/app/core-service/core/algorithms')


from qiskit import Aer
from qiskit import execute

from qae import qae


run_values = {'bernoulli_probability': '0.2'}


circuit = qae(run_values=run_values, task_log=print)


backend = Aer.get_backend('aer_simulator')

job = execute(circuit, backend, shots=1024)

counts = job.result().get_counts()

print(f'QAE circuit:\n{circuit}')
print(f'QAE counts: {counts}')