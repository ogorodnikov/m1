import sys 

sys.path.append('/home/ec2-user/environment/m1/app/core-service/core/algorithms')

from math import pi, sin

from qiskit import Aer
from qiskit import execute

from qae import qae


run_values = {'bernoulli_probability': '0.3'}


circuit = qae(run_values=run_values, task_log=print)


backend = Aer.get_backend('aer_simulator')

job = execute(circuit, backend, shots=1024)

counts = job.result().get_counts()



# Post-processing


qubits_count = 5

shots = sum(counts.values())

shots = 1024


measurements = dict()
samples = dict()

for state, count in counts.items():
    
    y = int(state.replace(" ", "")[:qubits_count][::-1], 2)
    
    probability = count / shots
    
    measurements[y] = probability
    
    amplitude = sin(y * pi / 2 ** qubits_count) ** 2
    
    rounded_amplitude = round(amplitude, ndigits=7)
    
    samples[rounded_amplitude] = samples.get(rounded_amplitude, 0.0) + probability
        

threshold = 1e-6

samples = {a: p for a, p in samples.items() if p > threshold}
measurements = {y: p for y, p in measurements.items() if p > threshold}
 

max_probability = 0

for amplitude, (mapped, prob) in zip(samples.keys(), samples.items()):
    if prob > max_probability:
        max_probability = prob
        estimation = amplitude
        estimation_processed = mapped


# Printouts

# print(f'QAE CUST circuit:\n{circuit}')
# print(f'QAE CUST counts: {counts}')

print(f'')
print(f'QAE CUST samples: {samples}')
print(f'QAE CUST measurements: {measurements}')
print(f'QAE CUST max_probability: {max_probability}')
print(f'QAE CUST estimation: {estimation}')
print(f'QAE CUST estimation_processed: {estimation_processed}')



