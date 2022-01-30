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



# Post-processing


# counts_decimals = {int(state[::-1], 2): count for state, count in counts.items()}
    
# counts_sum = sum(counts_decimals.values())

# states_weighted_sum = sum(state_decimal * count for state_decimal, count 
#                           in counts_decimals.items())

# states_average = states_weighted_sum / counts_sum

# first_state = next(iter(counts))

# precision = len(first_state)

# theta = states_average / 2 ** precision

# angle = theta * 2


# # Printouts

# print(f'QAE circuit:\n{circuit}')
# print(f'QAE counts: {counts}')

# print(f'QPE qpe_post_processing')

# print(f'QPE counts: {counts}')
# print(f'QPE counts_decimals: {counts_decimals}')
# print(f'QPE counts_sum: {counts_sum}')
# print(f'QPE states_weighted_sum: {states_weighted_sum}')
# print(f'QPE states_average: {states_average}')
# print(f'QPE first_state: {first_state}')

# print(f'QPE precision: {precision}')
# print(f'QPE theta: {theta}')
# print(f'QPE angle: {angle}')




# import numpy as np

# samples, measurements = self.evaluate_measurements(counts)

# samples = dict()
# measurements = dict()
# shots = 1024
# num_eval_qubits = 5

# for state, count in counts.items():
#     y = int(state.replace(" ", "")[: num_eval_qubits][::-1], 2)
#     probability = count / shots
#     measurements[y] = probability
#     a = np.round(np.power(np.sin(y * np.pi / 2 ** num_eval_qubits), 2), decimals=7)
#     samples[a] = samples.get(a, 0.0) + probability


# # determine the most likely estimate

# max_probability = 0

# for amplitude, (mapped, prob) in zip(samples.keys(), result.samples_processed.items()):
#     if prob > max_probability:
#         result.max_probability = prob
#         result.estimation = amplitude
#         result.estimation_processed = mapped

# # store the number of oracle queries
# result.num_oracle_queries = result.shots * (self._M - 1)




# Printouts

print(f'QAE circuit:\n{circuit}')
print(f'QAE counts: {counts}')
# 
# print(f'QAE samples: {samples}')
# print(f'QAE measurements: {measurements}')
# print(f'QAE max_probability: {max_probability}')



