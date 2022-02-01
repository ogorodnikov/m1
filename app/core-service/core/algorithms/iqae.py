from math import pi, sin, asin

from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister


from math import sqrt, log
from scipy.stats import beta

import numpy as np

from typing import Optional, Union, List, Tuple, Dict, cast

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
    
    
    # Reference IQAE
    
    from qiskit.algorithms import EstimationProblem

    problem = EstimationProblem(
        state_preparation=bernoulli_operator,
        grover_operator=bernoulli_diffuser,
        objective_qubits=[0],
    )
    
    from qiskit import Aer
    from qiskit.utils import QuantumInstance
    
    backend = Aer.get_backend("aer_simulator")
    quantum_instance = QuantumInstance(backend)
    
    from iqae_reference import IterativeAmplitudeEstimation
    
    accuracy = 0.01
    width_of_cofidence_interval = 0.05

    iae = IterativeAmplitudeEstimation(
        epsilon_target=accuracy,
        alpha=width_of_cofidence_interval,
        quantum_instance=quantum_instance,
    )
    
    iae.estimate(problem)
    
    

    # Custom IQAE
    
    state_preparation=bernoulli_operator
    grover_operator=bernoulli_diffuser
    objective_qubits=[0]
    
    confint_method = "beta"
    min_ratio = 2
    
    accuracy = 0.01
    width_of_cofidence_interval = 0.05

    epsilon = epsilon_target = accuracy
    alpha = width_of_cofidence_interval
    
    backend = Aer.get_backend("aer_simulator")
    quantum_instance = QuantumInstance(backend)
    

    
    def _find_next_k(
        k: int,
        upper_half_circle: bool,
        theta_interval: Tuple[float, float],
        min_ratio: float = 2.0,
    ) -> Tuple[int, bool]:
        """Find the largest integer k_next, such that the interval (4 * k_next + 2)*theta_interval
        lies completely in [0, pi] or [pi, 2pi], for theta_interval = (theta_lower, theta_upper).
    
        Args:
            k: The current power of the Q operator.
            upper_half_circle: Boolean flag of whether theta_interval lies in the
                upper half-circle [0, pi] or in the lower one [pi, 2pi].
            theta_interval: The current confidence interval for the angle theta,
                i.e. (theta_lower, theta_upper).
            min_ratio: Minimal ratio K/K_next allowed in the algorithm.
    
        Returns:
            The next power k, and boolean flag for the extrapolated interval.
    
        """
    
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
        
    
    def construct_circuit(k=0, measurement=False):
        
        num_qubits = max(
            state_preparation.num_qubits,
            grover_operator.num_qubits,
        )
        circuit = QuantumCircuit(num_qubits, name="circuit")
    
        # add classical register if needed
        if measurement:
            c = ClassicalRegister(len(objective_qubits))
            circuit.add_register(c)
    
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
            circuit.measure(objective_qubits, c[:])
    
        return circuit
    
    
    def _good_state_probability(
        problem,
        counts_or_statevector: Union[Dict[str, int], np.ndarray],
        num_state_qubits: int,
    ) -> Union[Tuple[int, float], float]:
        """Get the probability to measure '1' in the last qubit.
    
        Args:
            problem: The estimation problem, used to obtain the number of objective qubits and
                the ``is_good_state`` function.
            counts_or_statevector: Either a counts-dictionary (with one measured qubit only!) or
                the statevector returned from the statevector_simulator.
            num_state_qubits: The number of state qubits.
    
        Returns:
            If a dict is given, return (#one-counts, #one-counts/#all-counts),
            otherwise Pr(measure '1' in the last qubit).
        """
        if isinstance(counts_or_statevector, dict):
            one_counts = 0
            for state, counts in counts_or_statevector.items():
                if problem.is_good_state(state):
                    one_counts += counts
    
            return int(one_counts), one_counts / sum(counts_or_statevector.values())
        else:
            statevector = counts_or_statevector
            num_qubits = int(np.log2(len(statevector)))  # the total number of qubits
    
            # sum over all amplitudes where the objective qubit is 1
            prob = 0
            for i, amplitude in enumerate(statevector):
                # consider only state qubits and revert bit order
                bitstr = bin(i)[2:].zfill(num_qubits)[-num_state_qubits:][::-1]
                objectives = [bitstr[index] for index in problem.objective_qubits]
                if problem.is_good_state(objectives):
                    prob = prob + np.abs(amplitude) ** 2
    
            return prob
    
    
    def estimate(estimation_problem):
        
        # initialize memory variables
        powers = [0]  # list of powers k: Q^k, (called 'k' in paper)
        ratios = []  # list of multiplication factors (called 'q' in paper)
        theta_intervals = [[0, 1 / 4]]  # a priori knowledge of theta / 2 / pi
        a_intervals = [[0.0, 1.0]]  # a priori knowledge of the confidence interval of the estimate
        num_oracle_queries = 0
        num_one_shots = []
    
        # maximum number of rounds
        
        max_rounds = (
            int(np.log(min_ratio * np.pi / 8 / epsilon) / np.log(min_ratio)) + 1
        )
        upper_half_circle = True  # initially theta is in the upper half-circle
    
       
    
        num_iterations = 0  # keep track of the number of iterations
        shots = quantum_instance._run_config.shots  # number of shots per iteration
    
        # do while loop, keep in mind that we scaled theta mod 2pi such that it lies in [0,1]
        while theta_intervals[-1][1] - theta_intervals[-1][0] > epsilon / np.pi:
            num_iterations += 1
    
            # get the next k
            k, upper_half_circle = _find_next_k(
                powers[-1],
                upper_half_circle,
                theta_intervals[-1],  # type: ignore
                min_ratio=min_ratio,
            )
    
            # store the variables
            powers.append(k)
            ratios.append((2 * powers[-1] + 1) / (2 * powers[-2] + 1))
    
            # run measurements for Q^k A|0> circuit
            circuit = construct_circuit(k, measurement=True)
            ret = quantum_instance.execute(circuit)
            
            print(f'QAE circuit:\n{circuit}\n')  
    
            # get the counts and store them
            counts = ret.get_counts(circuit)
    
            # calculate the probability of measuring '1', 'prob' is a_i in the paper
            num_qubits = circuit.num_qubits - circuit.num_ancillas
            # type: ignore
            one_counts, prob = _good_state_probability(
                estimation_problem, counts, num_qubits
            )
    
            num_one_shots.append(one_counts)
    
            # track number of Q-oracle calls
            num_oracle_queries += shots * k
    
            # if on the previous iterations we have K_{i-1} == K_i, we sum these samples up
            j = 1  # number of times we stayed fixed at the same K
            round_shots = shots
            round_one_counts = one_counts
            if num_iterations > 1:
                while (
                    powers[num_iterations - j] == powers[num_iterations]
                    and num_iterations >= j + 1
                ):
                    j = j + 1
                    round_shots += shots
                    round_one_counts += num_one_shots[-j]
    
            # compute a_min_i, a_max_i
            if confint_method == "chernoff":
                a_i_min, a_i_max = chernoff_confidence_interval(prob, round_shots, max_rounds, alpha)
                
            else:  # 'beta'
                a_i_min, a_i_max = clopper_pearson_confidence_interval(
                    round_one_counts, round_shots, alpha / max_rounds
                )
    
            # compute theta_min_i, theta_max_i
            if upper_half_circle:
                theta_min_i = np.arccos(1 - 2 * a_i_min) / 2 / np.pi
                theta_max_i = np.arccos(1 - 2 * a_i_max) / 2 / np.pi
            else:
                theta_min_i = 1 - np.arccos(1 - 2 * a_i_max) / 2 / np.pi
                theta_max_i = 1 - np.arccos(1 - 2 * a_i_min) / 2 / np.pi
    
            # compute theta_u, theta_l of this iteration
            scaling = 4 * k + 2  # current K_i factor
            theta_u = (int(scaling * theta_intervals[-1][1]) + theta_max_i) / scaling
            theta_l = (int(scaling * theta_intervals[-1][0]) + theta_min_i) / scaling
            theta_intervals.append([theta_l, theta_u])
    
            # compute a_u_i, a_l_i
            a_u = np.sin(2 * np.pi * theta_u) ** 2
            a_l = np.sin(2 * np.pi * theta_l) ** 2
            a_u = cast(float, a_u)
            a_l = cast(float, a_l)
            a_intervals.append([a_l, a_u])
    
        # get the latest confidence interval for the estimate of a
        confidence_interval = tuple(a_intervals[-1])
    
        # the final estimate is the mean of the confidence interval
        estimation = np.mean(confidence_interval)
    
        epsilon_estimated = (confidence_interval[1] - confidence_interval[0]) / 2
        
        print(f'QAE alpha: {alpha}')
        print(f'QAE num_oracle_queries: {num_oracle_queries}')
        
        print(f'QAE estimation: {estimation}')
        print(f'QAE epsilon_estimated: {epsilon_estimated}')
        
        print(f'QAE confidence_interval: {confidence_interval}')
        print(f'QAE a_intervals: {a_intervals}')
        print(f'QAE theta_intervals: {theta_intervals}')
        
        print(f'QAE powers: {powers}')
        print(f'QAE ratios: {ratios}')
        
    
    estimate(problem)