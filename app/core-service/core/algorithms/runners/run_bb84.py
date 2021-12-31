import sys 

sys.path.append('/home/ec2-user/environment/m1/app/core-service/core/algorithms')


from qiskit import Aer
from qiskit import execute

from bb84 import bb84


run_values = {'secret': '1010'}

circuit = bb84(run_values=run_values, task_log=print)