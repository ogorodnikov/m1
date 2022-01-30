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

counts_total = sum(counts.values())


state_probabilities = dict()
amplitude_probabilities = dict()

for state_binary, count in counts.items():
    
    reversed_state = state_binary[::-1]
    state_decimal = int(reversed_state, 2)
    
    # State probability

    state_probability = count / counts_total
    state_probabilities[state_decimal] = state_probability
    
    # Amplitude
    
    amplitude = sin(state_decimal * pi / 2 ** qubits_count) ** 2
    rounded_amplitude = round(amplitude, ndigits=7)
    
    amplitude_probability = amplitude_probabilities.get(rounded_amplitude, 0.0)
    
    amplitude_probabilities[rounded_amplitude] = amplitude_probability + state_probability




# Estimation

# max_probability = 0

estimated_amplitude, estimated_amplitude_probability = max(amplitude_probabilities.items(), 
                                                           key=lambda item: item[1])

# for amplitude, (mapped, prob) in zip(amplitude_probabilities.keys(), amplitude_probabilities.items()):
#     if prob > max_probability:
#         max_probability = prob
#         estimation = amplitude
#         estimation_processed = mapped


# Printouts

# print(f'QAE CUST circuit:\n{circuit}')
# print(f'QAE CUST counts: {counts}')

print(f'')
print(f'QAE CUST state_probabilities: {state_probabilities}')
print(f'QAE CUST amplitude_probabilities: {amplitude_probabilities}')
print(f'QAE CUST max_probability: {max_probability}')
print(f'QAE CUST estimation: {estimation}')
print(f'QAE CUST estimation_processed: {estimation_processed}')

print(f'QAE CUST estimated_amplitude: {estimated_amplitude}')
print(f'QAE CUST estimated_amplitude_probability: {estimated_amplitude_probability}')



