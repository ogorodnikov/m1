import sys 

sys.path.append('/home/ec2-user/environment/m1/app/core-service/core/algorithms')


from qiskit import Aer
from qiskit import execute

from qae import qae


run_values = {'bernoulli_probability': '0.3'}


circuit = qae(run_values=run_values, task_log=print)


backend = Aer.get_backend('aer_simulator')

job = execute(circuit, backend, shots=1024)

counts = job.result().get_counts()



# Post-processing

num_eval_qubits = 5

circuit_results = counts
shots = sum(counts.values())



def evaluate_count_results(counts):
    
    import numpy as np
    from collections import OrderedDict
    
    # construct probabilities
    measurements = OrderedDict()
    samples = OrderedDict()
    
    shots = 1024

    for state, count in counts.items():
        y = int(state.replace(" ", "")[:num_eval_qubits][::-1], 2)
        probability = count / shots
        measurements[y] = probability
        a = np.round(np.power(np.sin(y * np.pi / 2 ** num_eval_qubits), 2), decimals=7)
        samples[a] = samples.get(a, 0.0) + probability
        
    print(f'QAE CUST samples: {samples}')
    print(f'QAE CUST measurements: {measurements}')

    return samples, measurements


def evaluate_measurements(circuit_results, threshold: float = 1e-6):

    samples, measurements = evaluate_count_results(circuit_results)

    # cutoff probabilities below the threshold
    samples = {a: p for a, p in samples.items() if p > threshold}
    measurements = {y: p for y, p in measurements.items() if p > threshold}

    return samples, measurements


samples, measurements = evaluate_measurements(circuit_results)

post_processing = lambda x: x

samples_processed = {
    post_processing(a): p for a, p in samples.items()
}

# determine the most likely estimate

max_probability = 0

for amplitude, (mapped, prob) in zip(samples.keys(), samples_processed.items()):
    if prob > max_probability:
        max_probability = prob
        estimation = amplitude
        estimation_processed = mapped

# store the number of oracle queries
num_oracle_queries = shots * (num_eval_qubits - 1)


# Printouts

print(f'QAE CUST circuit:\n{circuit}')
print(f'QAE CUST counts: {counts}')

print(f'QAE CUST samples: {samples}')
print(f'QAE CUST measurements: {measurements}')
print(f'QAE CUST max_probability: {max_probability}')
print(f'QAE CUST estimation: {estimation}')
print(f'QAE CUST estimation_processed: {estimation_processed}')



