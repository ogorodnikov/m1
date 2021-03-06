from typing import Optional, Union, List, Tuple, Dict, cast
import numpy as np
from scipy.stats import beta

from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.providers import BaseBackend, Backend
from qiskit.utils import QuantumInstance


class IterativeAmplitudeEstimation():

    def __init__(
        self,
        epsilon_target: float,
        alpha: float,
        confint_method: str = "beta",
        min_ratio: float = 2,
        quantum_instance: Optional[Union[QuantumInstance, BaseBackend, Backend]] = None,
    ) -> None:
        r"""
        The output of the algorithm is an estimate for the amplitude `a`, that with at least
        probability 1 - alpha has an error of epsilon. The number of A operator calls scales
        linearly in 1/epsilon (up to a logarithmic factor).

        Args:
            epsilon_target: Target precision for estimation target `a`, has values between 0 and 0.5
            alpha: Confidence level, the target probability is 1 - alpha, has values between 0 and 1
            confint_method: Statistical method used to estimate the confidence intervals in
                each iteration, can be 'chernoff' for the Chernoff intervals or 'beta' for the
                Clopper-Pearson intervals (default)
            min_ratio: Minimal q-ratio (:math:`K_{i+1} / K_i`) for FindNextK
            quantum_instance: Quantum Instance or Backend

        """
        
        self.quantum_instance = quantum_instance

        # store parameters
        self._epsilon = epsilon_target
        self._alpha = alpha
        self._min_ratio = min_ratio
        self._confint_method = confint_method

    @property
    def quantum_instance(self) -> Optional[QuantumInstance]:
        return self._quantum_instance

    @quantum_instance.setter
    def quantum_instance(
        self, quantum_instance: Union[QuantumInstance, BaseBackend, Backend]
    ) -> None:
        self._quantum_instance = quantum_instance

    @property
    def epsilon_target(self) -> float:
        return self._epsilon

    @epsilon_target.setter
    def epsilon_target(self, epsilon: float) -> None:
        self._epsilon = epsilon

    def _find_next_k(
        self,
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

    def construct_circuit(
        self, estimation_problem, k: int = 0, measurement: bool = False
    ) -> QuantumCircuit:
        r"""Construct the circuit :math:`\mathcal{Q}^k \mathcal{A} |0\rangle`.

        The A operator is the unitary specifying the QAE problem and Q the associated Grover
        operator.

        Args:
            estimation_problem: The estimation problem for which to construct the QAE circuit.
            k: The power of the Q operator.
            measurement: Boolean flag to indicate if measurements should be included in the
                circuits.

        Returns:
            The circuit implementing :math:`\mathcal{Q}^k \mathcal{A} |0\rangle`.
        """
        num_qubits = max(
            estimation_problem.state_preparation.num_qubits,
            estimation_problem.grover_operator.num_qubits,
        )
        circuit = QuantumCircuit(num_qubits, name="circuit")

        # add classical register if needed
        if measurement:
            c = ClassicalRegister(len(estimation_problem.objective_qubits))
            circuit.add_register(c)

        # add A operator
        circuit.compose(estimation_problem.state_preparation, inplace=True)

        # add Q^k
        if k != 0:
            circuit.compose(estimation_problem.grover_operator.power(k), inplace=True)

            # add optional measurement
        if measurement:
            # real hardware can currently not handle operations after measurements, which might
            # happen if the circuit gets transpiled, hence we're adding a safeguard-barrier
            circuit.barrier()
            circuit.measure(estimation_problem.objective_qubits, c[:])

        return circuit


    def _good_state_probability(
        self,
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


    def estimate(self, estimation_problem):
        
        # initialize memory variables
        powers = [0]  # list of powers k: Q^k, (called 'k' in paper)
        ratios = []  # list of multiplication factors (called 'q' in paper)
        theta_intervals = [[0, 1 / 4]]  # a priori knowledge of theta / 2 / pi
        a_intervals = [[0.0, 1.0]]  # a priori knowledge of the confidence interval of the estimate
        num_oracle_queries = 0
        num_one_shots = []

        # maximum number of rounds
        
        max_rounds = (
            int(np.log(self._min_ratio * np.pi / 8 / self._epsilon) / np.log(self._min_ratio)) + 1
        )
        upper_half_circle = True  # initially theta is in the upper half-circle

       

        num_iterations = 0  # keep track of the number of iterations
        shots = self._quantum_instance._run_config.shots  # number of shots per iteration

        # do while loop, keep in mind that we scaled theta mod 2pi such that it lies in [0,1]
        while theta_intervals[-1][1] - theta_intervals[-1][0] > self._epsilon / np.pi:
            num_iterations += 1

            # get the next k
            k, upper_half_circle = self._find_next_k(
                powers[-1],
                upper_half_circle,
                theta_intervals[-1],  # type: ignore
                min_ratio=self._min_ratio,
            )

            # store the variables
            powers.append(k)
            ratios.append((2 * powers[-1] + 1) / (2 * powers[-2] + 1))

            # run measurements for Q^k A|0> circuit
            circuit = self.construct_circuit(estimation_problem, k, measurement=True)
            ret = self._quantum_instance.execute(circuit)
            
            print(f'QAE circuit:\n{circuit}\n')  

            # get the counts and store them
            counts = ret.get_counts(circuit)

            # calculate the probability of measuring '1', 'prob' is a_i in the paper
            num_qubits = circuit.num_qubits - circuit.num_ancillas
            # type: ignore
            one_counts, prob = self._good_state_probability(
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
            if self._confint_method == "chernoff":
                a_i_min, a_i_max = chernoff_confidence_interval(prob, round_shots, max_rounds, self._alpha)
                
            else:  # 'beta'
                a_i_min, a_i_max = clopper_pearson_confidence_interval(
                    round_one_counts, round_shots, self._alpha / max_rounds
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

        alpha = self._alpha
        epsilon_estimated = (confidence_interval[1] - confidence_interval[0]) / 2
        
        print(f'QAE alpha: {alpha}')
        print(f'QAE num_oracle_queries: {num_oracle_queries}')
        
        print(f'QAE confidence_interval: {confidence_interval}')
        print(f'QAE a_intervals: {a_intervals}')
        print(f'QAE theta_intervals: {theta_intervals}')
        
        print(f'QAE powers: {powers}')
        print(f'QAE ratios: {ratios}')
        
        print(f'QAE epsilon_estimated: {epsilon_estimated}')        
        print(f'QAE estimation: {estimation}')
 

from math import sqrt, log

def chernoff_confidence_interval(current_estimate, shots_count, max_rounds, alpha_confidence_level):
    
    epsilon = sqrt(3 * log(2 * max_rounds / alpha_confidence_level) / shots_count)
    
    lower = max(0, current_estimate - epsilon)
    upper = min(1, current_estimate + epsilon)
    
    chernoff_confidence_interval = (lower, upper)

    print(f'QAE chernoff_confidence_interval: {chernoff_confidence_interval}')   
    
    return chernoff_confidence_interval


def clopper_pearson_confidence_interval(positive_counts, shots, alpha_confidence_level):
    
    lower, upper = 0, 1

    # if counts == 0, the beta quantile returns nan
    
    if positive_counts != 0:
        
        lower = beta.ppf(q=alpha_confidence_level / 2,
                         a=positive_counts, 
                         b=shots - positive_counts + 1)

    # if counts == shots, the beta quantile returns nan
    
    if positive_counts != shots:
        
        upper = beta.ppf(q=1 - alpha_confidence_level / 2,
                         a=positive_counts + 1,
                         b=shots - positive_counts)
        
    clopper_pearson_confidence_interval = (lower, upper)

    print(f'QAE clopper_pearson_confidence_interval: {clopper_pearson_confidence_interval}')  
    
    return clopper_pearson_confidence_interval
