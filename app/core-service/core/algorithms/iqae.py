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


def find_next_k(k, upper_half_circle, theta_interval, min_ratio):
    
    # initialize variables
    theta_l, theta_u = theta_interval
    old_scaling = 4 * k + 2  # current scaling factor, called K := (4k + 2)

    # the largest feasible scaling factor K cannot be larger than K_max,
    # which is bounded by the length of the current confidence interval
    max_scaling = int(1 / (2 * (theta_u - theta_l)))
    scaling = max_scaling - (max_scaling - 2) % 4  # bring into the form 4 * k_max + 2

    # find the largest feasible scaling factor K_next, and thus k_next
    while scaling >= min_ratio * old_scaling:
        theta_min = scaling * theta_l - int(scaling * theta_l)
        theta_max = scaling * theta_u - int(scaling * theta_u)

        if theta_min <= theta_max <= 0.5 and theta_min <= 0.5:
            # the extrapolated theta interval is in the upper half-circle
            upper_half_circle = True
            return int((scaling - 2) / 4), upper_half_circle

        elif theta_max >= 0.5 and theta_max >= theta_min >= 0.5:
            # the extrapolated theta interval is in the upper half-circle
            upper_half_circle = False
            return int((scaling - 2) / 4), upper_half_circle

        scaling -= 4

    # if we do not find a feasible k, return the old one
    return int(k), upper_half_circle


def build_iqae_circuit(state_preparation,
                       grover_operator,
                       objective_qubits,
                       k=0,
                       measurement=False):
    
    all_qubits_count = max(state_preparation.num_qubits,
                           grover_operator.num_qubits)
                           
    measurement_bits_count = len(objective_qubits)
    
    iqae_register = QuantumRegister(all_qubits_count, 'iqae')
                     
    circuit = QuantumCircuit(iqae_register, name="IQAE")
    
    # circuit = QuantumCircuit(qubits_count, name="IQAE")

    # add classical register if needed
    if measurement:
        
        measurement_register = ClassicalRegister(measurement_bits_count, 'measure')
        
        # c = ClassicalRegister(measurement_bits_count)
        # circuit.add_register(c)
        
        circuit.add_register(measurement_register)

    # add A operator
    circuit.compose(state_preparation, inplace=True)

    # add Q^k
    if k != 0:
        circuit.compose(grover_operator.power(k), inplace=True)

        # add optional measurement
    if measurement:
        # real hardware can currently not handle operations after measurements, which might
        # happen if the circuit gets transpiled, hence we're adding a safeguard-barrier
        circuit.barrier()
        circuit.measure(objective_qubits, measurement_register[:])

    return circuit
    
    

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
    a_intervals = [[0.0, 1.0]]
    oracle_queries_count = 0
    one_shots_counts = []
    upper_half_circle = True

    iteration_number = 0
    
    max_rounds = int(log(min_ratio * pi / 8 / epsilon) / log(min_ratio)) + 1
    
    theta_interval = theta_intervals[-1]
    theta_lower, theta_upper = theta_interval
    theta_delta = theta_upper - theta_lower
    
    while theta_delta > epsilon / pi:
        
        iteration_number += 1
        
        last_k = powers[-1]

        k, upper_half_circle = find_next_k(
            last_k,
            upper_half_circle,
            theta_interval,
            min_ratio=min_ratio,
        )

        powers.append(k)
        
        multiplication_factor = (2 * k + 1) / (2 * last_k + 1)
        
        multiplication_factors.append(multiplication_factor)

        iqae_circuit = build_iqae_circuit(state_preparation,
                                          grover_operator,
                                          objective_qubits,
                                          k,
                                          measurement=True)
                                     
        result = quantum_instance.execute(iqae_circuit)
        
        counts = result.get_counts()

        one_counts = sum(state_counts for state, state_counts in counts.items()
                         if is_good_state(state))
                         
        counts_total = sum(counts.values())
        
        probability_of_measuring_one = one_counts / counts_total
        

        one_shots_counts.append(one_counts)

        oracle_queries_count += shots * k

        # if on the previous iterations we have K_{i-1} == K_i, we sum these samples up
        j = 1  # number of times we stayed fixed at the same K
        round_shots = shots
        round_one_counts = one_counts
        if iteration_number > 1:
            while (
                powers[iteration_number - j] == powers[iteration_number]
                and iteration_number >= j + 1
            ):
                j = j + 1
                round_shots += shots
                round_one_counts += one_shots_counts[-j]

        # Ai

        if confint_method == "chernoff":
            a_i_min, a_i_max = chernoff_confidence_interval(probability_of_measuring_one,
                                                            round_shots,
                                                            max_rounds,
                                                            alpha)
            
        elif confint_method == "clopper_pearson":
            
            alpha_confidence_level = alpha / max_rounds
            
            a_i_min, a_i_max = clopper_pearson_confidence_interval(round_one_counts, 
                                                                   round_shots,
                                                                   alpha_confidence_level)

        # Theta
        
        if upper_half_circle:
            theta_min_i = acos(1 - 2 * a_i_min) / 2 / pi
            theta_max_i = acos(1 - 2 * a_i_max) / 2 / pi
        else:
            theta_min_i = 1 - acos(1 - 2 * a_i_max) / 2 / pi
            theta_max_i = 1 - acos(1 - 2 * a_i_min) / 2 / pi

        scaling = 4 * k + 2
        
        theta_u = (int(scaling * theta_intervals[-1][1]) + theta_max_i) / scaling
        theta_l = (int(scaling * theta_intervals[-1][0]) + theta_min_i) / scaling

        theta_delta = theta_u - theta_l
        
        theta_interval = [theta_l, theta_u]
        
        theta_intervals.append(theta_interval)

        # Amplitude
        
        a_upper = sin(2 * pi * theta_u) ** 2
        a_lower = sin(2 * pi * theta_l) ** 2
        
        a_interval = [a_lower, a_upper]
        a_intervals.append(a_interval)
        
        task_log(f'QAE iqae_circuit:\n{iqae_circuit}\n')


    # Estimate

    confidence_interval = a_interval
    
    confidence_interval_lower, confidence_interval_upper = confidence_interval

    estimation = sum(confidence_interval) / 2

    epsilon_estimated = (confidence_interval_upper - confidence_interval_lower) / 2
    
    
    # Logs
    
    task_log(f'QAE alpha: {alpha}')
    
    task_log(f'QAE oracle_queries_count: {oracle_queries_count}')
    task_log(f'QAE one_shots_counts: {one_shots_counts}')
    task_log(f'QAE iteration_number: {iteration_number}')
    
    task_log(f'QAE confidence_interval: {confidence_interval}')
    task_log(f'QAE a_intervals: {a_intervals}')
    task_log(f'QAE theta_intervals: {theta_intervals}')
    
    task_log(f'QAE powers: {powers}')
    task_log(f'QAE multiplication_factors: {multiplication_factors}')

    task_log(f'QAE epsilon_estimated: {epsilon_estimated}')
    task_log(f'QAE estimation: {estimation}')
