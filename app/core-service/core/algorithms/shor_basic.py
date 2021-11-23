import math
import numpy as np
from qiskit import Aer
from qiskit.utils import QuantumInstance
# from qiskit.algorithms import Shor


"""   https://github.com/Qiskit/qiskit-tutorials/blob/0994a317891cf688f55ebed5a06f8a227c8440ac/tutorials/algorithms/08_factorizers.ipynb   """
"""   https://github.com/Qiskit/qiskit-terra/blob/main/qiskit/algorithms/factorizers/shor.py   """



def run_shor():
    
    number = 9
    base = 2
    
    print(f"SHOR number: {number}")
    print(f"SHOR number: {number}")
    
    if (number < 3 or 
        number % 2 == 0 or
        base < 2 or
        base >= number or
        math.gcd(base, number) != 1):
        
        raise ValueError("Incorrect input values")
    
    backend = Aer.get_backend('aer_simulator')
    
    quantum_instance = QuantumInstance(backend, shots=1024)
    
    shor = Shor(quantum_instance=quantum_instance)
    
    result = shor.factor(number)
    
    print(f"SHOR Result factors: {result.factors}")
    print(f"SHOR Result factors: {result.factors[0]}")
    
    theoretical_qubits_count = 4 * math.ceil(math.log(number, 2)) + 2
    actual_qubits_count = shor.construct_circuit(number).num_qubits
    
    print(f'SHOR theoretical_qubits_count: {theoretical_qubits_count}')
    print(f'SHOR actual_qubits_count: {actual_qubits_count}')





"""Shor's factoring algorithm."""

import array
import fractions
import logging
import math
import sys
from typing import Optional, Union, List, Tuple

import numpy as np

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit import Gate, Instruction, ParameterVector
from qiskit.circuit.library import QFT
from qiskit.providers import Backend
from qiskit.providers import BaseBackend
from qiskit.quantum_info import partial_trace
from qiskit.utils import summarize_circuits
from qiskit.utils.arithmetic import is_power
from qiskit.utils.quantum_instance import QuantumInstance
from qiskit.algorithms.algorithm_result import AlgorithmResult
from qiskit.algorithms.exceptions import AlgorithmError

logger = logging.getLogger(__name__)


class Shor:

    def __init__(self, quantum_instance):
        """
        Args:
            quantum_instance: Quantum Instance or Backend
        """
        self._quantum_instance = None
        if quantum_instance:
            self.quantum_instance = quantum_instance

    @property
    def quantum_instance(self) -> Optional[QuantumInstance]:
        """Returns quantum instance."""
        return self._quantum_instance

    @quantum_instance.setter
    def quantum_instance(
        self, quantum_instance: Union[QuantumInstance, BaseBackend, Backend]
    ) -> None:
        """Sets quantum instance."""
        if isinstance(quantum_instance, (BaseBackend, Backend)):
            quantum_instance = QuantumInstance(quantum_instance)
        self._quantum_instance = quantum_instance

    @staticmethod
    def _get_angles(a: int, n: int) -> np.ndarray:
        """Calculates the array of angles to be used in the addition in Fourier Space."""
        bits_little_endian = (bin(int(a))[2:].zfill(n))[::-1]

        angles = np.zeros(n)
        for i in range(n):
            for j in range(i + 1):
                k = i - j
                if bits_little_endian[j] == "1":
                    angles[i] += pow(2, -k)

        return angles * np.pi

    @staticmethod
    def _phi_add_gate(angles: Union[np.ndarray, ParameterVector]) -> Gate:
        """Gate that performs addition by a in Fourier Space."""
        circuit = QuantumCircuit(len(angles), name="phi_add_a")
        for i, angle in enumerate(angles):
            circuit.p(angle, i)
        return circuit.to_gate()

    def _double_controlled_phi_add_mod_N(
        self,
        angles: Union[np.ndarray, ParameterVector],
        c_phi_add_N: Gate,
        iphi_add_N: Gate,
        qft: Gate,
        iqft: Gate,
    ) -> QuantumCircuit:
        """Creates a circuit which implements double-controlled modular addition by a."""
        ctrl_qreg = QuantumRegister(2, "ctrl")
        b_qreg = QuantumRegister(len(angles), "b")
        flag_qreg = QuantumRegister(1, "flag")

        circuit = QuantumCircuit(ctrl_qreg, b_qreg, flag_qreg, name="ccphi_add_a_mod_N")

        cc_phi_add_a = self._phi_add_gate(angles).control(2)
        cc_iphi_add_a = cc_phi_add_a.inverse()

        circuit.append(cc_phi_add_a, [*ctrl_qreg, *b_qreg])

        circuit.append(iphi_add_N, b_qreg)

        circuit.append(iqft, b_qreg)
        circuit.cx(b_qreg[-1], flag_qreg[0])
        circuit.append(qft, b_qreg)

        circuit.append(c_phi_add_N, [*flag_qreg, *b_qreg])

        circuit.append(cc_iphi_add_a, [*ctrl_qreg, *b_qreg])

        circuit.append(iqft, b_qreg)
        circuit.x(b_qreg[-1])
        circuit.cx(b_qreg[-1], flag_qreg[0])
        circuit.x(b_qreg[-1])
        circuit.append(qft, b_qreg)

        circuit.append(cc_phi_add_a, [*ctrl_qreg, *b_qreg])

        return circuit

    def _controlled_multiple_mod_N(
        self, n: int, N: int, a: int, c_phi_add_N: Gate, iphi_add_N: Gate, qft: Gate, iqft: Gate
    ) -> Instruction:
        """Implements modular multiplication by a as an instruction."""
        ctrl_qreg = QuantumRegister(1, "ctrl")
        x_qreg = QuantumRegister(n, "x")
        b_qreg = QuantumRegister(n + 1, "b")
        flag_qreg = QuantumRegister(1, "flag")

        circuit = QuantumCircuit(ctrl_qreg, x_qreg, b_qreg, flag_qreg, name="cmult_a_mod_N")

        angle_params = ParameterVector("angles", length=n + 1)
        modulo_adder = self._double_controlled_phi_add_mod_N(
            angle_params, c_phi_add_N, iphi_add_N, qft, iqft
        )

        def append_adder(adder: QuantumCircuit, constant: int, idx: int):
            partial_constant = (pow(2, idx, N) * constant) % N
            angles = self._get_angles(partial_constant, n + 1)
            bound = adder.assign_parameters({angle_params: angles})
            circuit.append(bound, [*ctrl_qreg, x_qreg[idx], *b_qreg, *flag_qreg])

        circuit.append(qft, b_qreg)

        # perform controlled addition by a on the aux register in Fourier space
        for i in range(n):
            append_adder(modulo_adder, a, i)

        circuit.append(iqft, b_qreg)

        # perform controlled subtraction by a in Fourier space on both the aux and down register
        for i in range(n):
            circuit.cswap(ctrl_qreg, x_qreg[i], b_qreg[i])

        circuit.append(qft, b_qreg)

        a_inv = pow(a, -1, mod=N) if sys.version_info >= (3, 8) else self.modinv(a, N)

        modulo_adder_inv = modulo_adder.inverse()
        for i in reversed(range(n)):
            append_adder(modulo_adder_inv, a_inv, i)

        circuit.append(iqft, b_qreg)

        return circuit.to_instruction()

    def _power_mod_N(self, n: int, N: int, a: int) -> Instruction:
        """Implements modular exponentiation a^x as an instruction."""
        up_qreg = QuantumRegister(2 * n, name="up")
        down_qreg = QuantumRegister(n, name="down")
        aux_qreg = QuantumRegister(n + 2, name="aux")

        circuit = QuantumCircuit(up_qreg, down_qreg, aux_qreg, name=f"{a}^x mod {N}")

        qft = QFT(n + 1, do_swaps=False).to_gate()
        iqft = qft.inverse()

        # Create gates to perform addition/subtraction by N in Fourier Space
        phi_add_N = self._phi_add_gate(self._get_angles(N, n + 1))
        iphi_add_N = phi_add_N.inverse()
        c_phi_add_N = phi_add_N.control(1)

        # Apply the multiplication gates as showed in
        # the report in order to create the exponentiation
        for i in range(2 * n):
            partial_a = pow(a, pow(2, i), N)
            modulo_multiplier = self._controlled_multiple_mod_N(
                n, N, partial_a, c_phi_add_N, iphi_add_N, qft, iqft
            )
            circuit.append(modulo_multiplier, [up_qreg[i], *down_qreg, *aux_qreg])

        return circuit.to_instruction()


    def construct_circuit(self, N: int, a: int = 2, measurement: bool = False) -> QuantumCircuit:
        """Construct quantum part of the algorithm.
        Args:
            N: The odd integer to be factored, has a min. value of 3.
            a: Any integer that satisfies 1 < a < N and gcd(a, N) = 1.
            measurement: Boolean flag to indicate if measurement should be included in the circuit.
        Returns:
            Quantum circuit.
        """

        # Get n value used in Shor's algorithm, to know how many qubits are used
        n = N.bit_length()

        # quantum register where the sequential QFT is performed
        up_qreg = QuantumRegister(2 * n, name="up")
        # quantum register where the multiplications are made
        down_qreg = QuantumRegister(n, name="down")
        # auxiliary quantum register used in addition and multiplication
        aux_qreg = QuantumRegister(n + 2, name="aux")

        # Create Quantum Circuit
        circuit = QuantumCircuit(up_qreg, down_qreg, aux_qreg, name=f"Shor(N={N}, a={a})")

        # Create maximal superposition in top register
        circuit.h(up_qreg)

        # Initialize down register to 1
        circuit.x(down_qreg[0])

        # Apply modulo exponentiation
        modulo_power = self._power_mod_N(n, N, a)
        circuit.append(modulo_power, circuit.qubits)

        # Apply inverse QFT
        iqft = QFT(len(up_qreg)).inverse().to_gate()
        circuit.append(iqft, up_qreg)

        if measurement:
            up_cqreg = ClassicalRegister(2 * n, name="m")
            circuit.add_register(up_cqreg)
            circuit.measure(up_qreg, up_cqreg)

        logger.info(summarize_circuits(circuit))

        return circuit

    @staticmethod
    def modinv(a: int, m: int) -> int:
        """Returns the modular multiplicative inverse of a with respect to the modulus m."""

        def egcd(a: int, b: int) -> Tuple[int, int, int]:
            if a == 0:
                return b, 0, 1
            else:
                g, y, x = egcd(b % a, a)
                return g, x - (b // a) * y, y

        g, x, _ = egcd(a, m)
        if g != 1:
            raise ValueError(
                "The greatest common divisor of {} and {} is {}, so the "
                "modular inverse does not exist.".format(a, m, g)
            )
        return x % m

    def _get_factors(self, N: int, a: int, measurement: str) -> Optional[List[int]]:
        """Apply the continued fractions to find r and the gcd to find the desired factors."""
        x_final = int(measurement, 2)
        logger.info("In decimal, x_final value for this result is: %s.", x_final)

        if x_final <= 0:
            fail_reason = "x_final value is <= 0, there are no continued fractions."
        else:
            fail_reason = None
            logger.debug("Running continued fractions for this case.")

        # Calculate T and x/T
        T_upper = len(measurement)
        T = pow(2, T_upper)
        x_over_T = x_final / T

        # Cycle in which each iteration corresponds to putting one more term in the
        # calculation of the Continued Fraction (CF) of x/T

        # Initialize the first values according to CF rule
        i = 0
        b = array.array("i")
        t = array.array("f")

        b.append(math.floor(x_over_T))
        t.append(x_over_T - b[i])

        exponential = 0.0
        while i < N and fail_reason is None:
            # From the 2nd iteration onwards, calculate the new terms of the CF based
            # on the previous terms as the rule suggests
            if i > 0:
                b.append(math.floor(1 / t[i - 1]))
                t.append((1 / t[i - 1]) - b[i])  # type: ignore

            # Calculate the denominator of the CF using the known terms
            denominator = self._calculate_continued_fraction(b)

            # Increment i for next iteration
            i += 1

            if denominator % 2 == 1:
                logger.debug("Odd denominator, will try next iteration of continued fractions.")
                continue

            # Denominator is even, try to get factors of N
            # Get the exponential a^(r/2)

            if denominator < 1000:
                exponential = pow(a, denominator / 2)

            # Check if the value is too big or not
            if exponential > 1000000000:
                fail_reason = "denominator of continued fraction is too big."
            else:
                # The value is not too big,
                # get the right values and do the proper gcd()
                putting_plus = int(exponential + 1)
                putting_minus = int(exponential - 1)
                one_factor = math.gcd(putting_plus, N)
                other_factor = math.gcd(putting_minus, N)

                # Check if the factors found are trivial factors or are the desired factors
                if any(factor in {1, N} for factor in (one_factor, other_factor)):
                    logger.debug("Found just trivial factors, not good enough.")
                    # Check if the number has already been found,
                    # (use i - 1 because i was already incremented)
                    if t[i - 1] == 0:
                        fail_reason = "the continued fractions found exactly x_final/(2^(2n))."
                else:
                    # Successfully factorized N
                    return sorted((one_factor, other_factor))

        # Search for factors failed, write the reason for failure to the debug logs
        logger.debug(
            "Cannot find factors from measurement %s because %s",
            measurement,
            fail_reason or "it took too many attempts.",
        )
        return None

    @staticmethod
    def _calculate_continued_fraction(b: array.array) -> int:
        """Calculate the continued fraction of x/T from the current terms of expansion b."""

        x_over_T = 0

        for i in reversed(range(len(b) - 1)):
            x_over_T = 1 / (b[i + 1] + x_over_T)

        x_over_T += b[0]

        # Get the denominator from the value obtained
        frac = fractions.Fraction(x_over_T).limit_denominator()

        logger.debug("Approximation number %s of continued fractions:", len(b))
        logger.debug("Numerator:%s \t\t Denominator: %s.", frac.numerator, frac.denominator)
        return frac.denominator
        

    def factor(self, N, a = 2):

        if self.quantum_instance is None:
            raise AlgorithmError(
                "A QuantumInstance or Backend must be supplied to run the quantum algorithm."
            )

        result = ShorResult()

        # check if the input integer N is a power
        tf, b, p = is_power(N, return_decomposition=True)
        if tf:
            logger.info("The input integer is a power: %s=%s^%s.", N, b, p)
            result.factors.append(b)

        if not result.factors:
            logger.debug("Running with N=%s and a=%s.", N, a)

            if self._quantum_instance.is_statevector:
                # Get n value used in Shor's algorithm, to know how many qubits are used
                n = N.bit_length()

                circuit = self.construct_circuit(N=N, a=a, measurement=False)
                logger.warning(
                    "The statevector_simulator might lead to "
                    "subsequent computation using too much memory."
                )
                result = self._quantum_instance.execute(circuit)
                complete_state_vec = result.get_statevector(circuit)
                # TODO: this uses too much memory
                up_qreg_density_mat = partial_trace(complete_state_vec, range(2 * n, 4 * n + 2))
                up_qreg_density_mat_diag = np.diag(up_qreg_density_mat)

                counts = {}
                for i, v in enumerate(up_qreg_density_mat_diag):
                    if not v == 0:
                        counts[bin(int(i))[2:].zfill(2 * n)] = v ** 2
            else:
                circuit = self.construct_circuit(N=N, a=a, measurement=True)
                counts = self._quantum_instance.execute(circuit).get_counts(circuit)

            result.total_counts = len(counts)

            # For each simulation result, print proper info to user
            # and try to calculate the factors of N
            for measurement in list(counts.keys()):
                # Get the x_final value from the final state qubits
                logger.info("------> Analyzing result %s.", measurement)
                factors = self._get_factors(N, a, measurement)

                if factors:
                    logger.info("Found factors %s from measurement %s.", factors, measurement)
                    result.successful_counts = result.successful_counts + 1
                    if factors not in result.factors:
                        result.factors.append(factors)

        return result


class ShorResult(AlgorithmResult):
    """Shor Result."""

    def __init__(self) -> None:
        super().__init__()
        self._factors = []
        self._total_counts = 0
        self._successful_counts = 0

    @property
    def factors(self) -> List[List[int]]:
        """returns factors"""
        return self._factors

    @factors.setter
    def factors(self, value: List[List[int]]) -> None:
        """set factors"""
        self._factors = value

    @property
    def total_counts(self) -> int:
        """returns total counts"""
        return self._total_counts

    @total_counts.setter
    def total_counts(self, value: int) -> None:
        """set total counts"""
        self._total_counts = value

    @property
    def successful_counts(self) -> int:
        """returns successful counts"""
        return self._successful_counts

    @successful_counts.setter
    def successful_counts(self, value: int) -> None:
        """set successful counts"""
        self._successful_counts = value
        

run_shor()