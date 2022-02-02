from math import pi, sin, asin, acos, log, log2, sqrt

from scipy.stats import beta

from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister

from qiskit import Aer

from qiskit.providers import BaseBackend, Backend
from qiskit.utils import QuantumInstance




def chernoff_confidence_interval(current_estimate, shots_count, max_rounds, alpha_confidence_level):
    
    epsilon = sqrt(3 * log(2 * max_rounds / alpha_confidence_level) / shots_count)
    
    lower = max(0, current_estimate - epsilon)
    upper = min(1, current_estimate + epsilon)
    
    chernoff_confidence_interval = (lower, upper)

    print(f'QAE chernoff_confidence_interval: {chernoff_confidence_interval}')   
    
    return chernoff_confidence_interval


def clopper_pearson_confidence_interval(positive_counts, shots, alpha_confidence_level):
    
    lower, upper = 0, 1

    # if counts == 0, the beta quantile returns NaN
    
    if positive_counts != 0:
        
        lower = beta.ppf(q=alpha_confidence_level / 2,
                         a=positive_counts, 
                         b=shots - positive_counts + 1)

    # if counts == shots, the beta quantile returns NaN
    
    if positive_counts != shots:
        
        upper = beta.ppf(q=1 - alpha_confidence_level / 2,
                         a=positive_counts + 1,
                         b=shots - positive_counts)
        
    clopper_pearson_confidence_interval = (lower, upper)

    print(f'QAE clopper_pearson_confidence_interval: {clopper_pearson_confidence_interval}')  
    
    return clopper_pearson_confidence_interval


def find_next_power(power, is_upper_half_circle, theta_interval, min_ratio):
    
    # initialize variables
    theta_lower, theta_upper = theta_interval
    old_scaling = 4 * power + 2  # current scaling factor, called K := (4k + 2)

    # the largest feasible scaling factor K cannot be larger than K_max,
    # which is bounded by the length of the current confidence interval
    max_scaling = int(1 / (2 * (theta_upper - theta_lower)))
    scaling = max_scaling - (max_scaling - 2) % 4  # bring into the form 4 * k_max + 2

    # find the largest feasible scaling factor K_next, and thus k_next
    while scaling >= min_ratio * old_scaling:
        theta_min = scaling * theta_lower - int(scaling * theta_lower)
        theta_max = scaling * theta_upper - int(scaling * theta_upper)

        if theta_min <= theta_max <= 0.5 and theta_min <= 0.5:
            # the extrapolated theta interval is in the upper half-circle
            is_upper_half_circle = True
            return int((scaling - 2) / 4), is_upper_half_circle

        elif theta_max >= 0.5 and theta_max >= theta_min >= 0.5:
            # the extrapolated theta interval is in the upper half-circle
            is_upper_half_circle = False
            return int((scaling - 2) / 4), is_upper_half_circle

        scaling -= 4
        
    power = int(power)

    return power, is_upper_half_circle


def build_iqae_circuit(state_preparation,
                       grover_operator,
                       objective_qubits,
                       k=0,
                       measurement=False):
    
    all_qubits_count = max(state_preparation.num_qubits,
                           grover_operator.num_qubits)
                           
    measurement_bits_count = len(objective_qubits)
    
    iqae_register = QuantumRegister(all_qubits_count, 'iqae')
                     
    iqae_circuit = QuantumCircuit(iqae_register, name="IQAE")
    
    iqae_circuit.append(state_preparation, iqae_register)

    if k != 0:
        iqae_circuit.append(grover_operator.power(k), iqae_register)
        
    if measurement:
        
        measurement_register = ClassicalRegister(measurement_bits_count, 'measure')
        iqae_circuit.add_register(measurement_register)
        
        iqae_circuit.barrier()
        iqae_circuit.measure(iqae_register, measurement_register)

    return iqae_circuit
    
    

def iqae(run_values, task_log):
    
    """
    Create Iterative Quantum Amplitude Estimation (IQAE) circuit
    
    https://qiskit.org/documentation/finance/tutorials/00_amplitude_estimation.html
    
    """
    
    # Input
    
    input_bernoulli_probability = run_values.get('bernoulli_probability')
    input_precision = run_values.get('precision')
    
    bernoulli_probability = float(input_bernoulli_probability)
    precision = int(input_precision)
    
    
    # Bernoulli Circuits
    
    theta_p = 2 * asin(bernoulli_probability ** 0.5)
    
    bernoulli_operator = QuantumCircuit(1)
    bernoulli_operator.ry(theta_p, 0)
    
    bernoulli_diffuser = QuantumCircuit(1)
    bernoulli_diffuser.ry(2 * theta_p, 0)
    
    controlled_bernoulli_diffuser = bernoulli_diffuser.control()
    controlled_bernoulli_diffuser.name = 'Controlled Bernoulli Diffuser'
    
    bernoulli_operator.name = 'Bernoulli Operator'
    bernoulli_diffuser.name = 'Bernoulli Diffuser'
    controlled_bernoulli_diffuser.name = 'CBD'
    
    
    # Problem
    
    state_preparation = bernoulli_operator
    grover_operator = bernoulli_diffuser
    objective_qubits = [0]
    is_good_state = lambda x: all(bit == "1" for bit in x)
    
    # Parameters
    
    confint_method = "clopper_pearson"
    min_ratio = 2
    
    accuracy = 0.01
    width_of_cofidence_interval = 0.05

    epsilon = epsilon_target = accuracy
    alpha = width_of_cofidence_interval
    
    shots = 1024
    backend = Aer.get_backend("aer_simulator")
    quantum_instance = QuantumInstance(backend)

        
    # Initialization
    
    powers = [0]
    multiplication_factors = []
    theta_intervals = [[0, 1 / 4]]
    amplitude_intervals = [[0.0, 1.0]]
    oracle_queries_count = 0
    one_shots_counts = []
    is_upper_half_circle = True

    iteration_number = 0
    
    max_rounds = int(log(min_ratio * pi / 8 / epsilon) / log(min_ratio)) + 1
    
    theta_interval = theta_intervals[-1]
    theta_lower, theta_upper = theta_interval
    theta_delta = theta_upper - theta_lower
    
    
    # Iterations
    
    while theta_delta > epsilon / pi:
        
        iteration_number += 1
        
        last_power = powers[-1]

        power, is_upper_half_circle = find_next_power(
            last_power,
            is_upper_half_circle,
            theta_interval,
            min_ratio=min_ratio,
        )

        powers.append(power)
        
        multiplication_factor = (2 * power + 1) / (2 * last_power + 1)
        
        multiplication_factors.append(multiplication_factor)

        iqae_circuit = build_iqae_circuit(state_preparation,
                                          grover_operator,
                                          objective_qubits,
                                          power,
                                          measurement=True)
                                     
        result = quantum_instance.execute(iqae_circuit)
        
        counts = result.get_counts()

        one_counts = sum(state_counts for state, state_counts in counts.items()
                         if is_good_state(state))
                         
        counts_total = sum(counts.values())
        
        probability_of_measuring_one = one_counts / counts_total

        one_shots_counts.append(one_counts)

        oracle_queries_count += shots * power
        

        # Amplitude range

        if confint_method == "chernoff":
            
            amplitude_range = chernoff_confidence_interval(probability_of_measuring_one,
                                                           shots,
                                                           max_rounds,
                                                           alpha)
            
        elif confint_method == "clopper_pearson":
            
            alpha_confidence_level = alpha / max_rounds
            
            amplitude_range = clopper_pearson_confidence_interval(one_counts, 
                                                                  shots,
                                                                  alpha_confidence_level)
                                                                   
        amplitude_min, amplitude_max = amplitude_range
        

        # Theta
        
        if is_upper_half_circle:
            theta_min = acos(1 - 2 * amplitude_min) / 2 / pi
            theta_max = acos(1 - 2 * amplitude_max) / 2 / pi
        else:
            theta_min = 1 - acos(1 - 2 * amplitude_max) / 2 / pi
            theta_max = 1 - acos(1 - 2 * amplitude_min) / 2 / pi

        scaling = 4 * power + 2
        
        last_theta_interval = theta_intervals[-1]
        last_theta_lower, last_theta_upper = last_theta_interval
        
        theta_upper = (int(scaling * last_theta_upper) + theta_max) / scaling
        theta_lower = (int(scaling * last_theta_lower) + theta_min) / scaling

        theta_delta = theta_upper - theta_lower
        
        theta_interval = [theta_lower, theta_upper]
        
        theta_intervals.append(theta_interval)
        

        # Amplitude
        
        amplitude_upper = sin(2 * pi * theta_upper) ** 2
        amplitude_lower = sin(2 * pi * theta_lower) ** 2
        
        amplitude_interval = [amplitude_lower, amplitude_upper]
        amplitude_intervals.append(amplitude_interval)
        
        task_log(f'QAE iqae_circuit:\n{iqae_circuit}\n')


    # Estimate

    confidence_interval = amplitude_interval
    confidence_interval_lower, confidence_interval_upper = confidence_interval

    epsilon_estimated = (confidence_interval_upper - confidence_interval_lower) / 2
    
    amplitude_estimated = sum(confidence_interval) / 2

    
    # Logs
    
    task_log(f'QAE Input data:\n')
    task_log(f'QAE epsilon: {epsilon}')
    task_log(f'QAE accuracy: {accuracy}')
    task_log(f'QAE alpha: {alpha}\n')

    task_log(f'QAE Processing:\n')    
    task_log(f'QAE iteration_number: {iteration_number}')    
    task_log(f'QAE oracle_queries_count: {oracle_queries_count}')
    task_log(f'QAE one_shots_counts: {one_shots_counts}')
    task_log(f'QAE multiplication_factors: {multiplication_factors}')
    task_log(f'QAE powers: {powers}\n')
    
    task_log(f'QAE theta_intervals: {theta_intervals}')    
    task_log(f'QAE amplitude_intervals: {amplitude_intervals}')
    task_log(f'QAE confidence_interval: {confidence_interval}\n')

    task_log(f'QAE Results:\n') 
    task_log(f'QAE epsilon_estimated: {epsilon_estimated}')
    task_log(f'QAE amplitude_estimated: {amplitude_estimated}')
