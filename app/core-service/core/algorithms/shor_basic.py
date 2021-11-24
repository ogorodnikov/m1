import math
import numpy as np
from qiskit import Aer
from qiskit.utils import QuantumInstance
# from qiskit.algorithms import Shor

from qft import build_qft_circuit


"""   https://github.com/Qiskit/qiskit-tutorials/blob/0994a317891cf688f55ebed5a06f8a227c8440ac/tutorials/algorithms/08_factorizers.ipynb   """
"""   https://github.com/Qiskit/qiskit-terra/blob/main/qiskit/algorithms/factorizers/shor.py   """



def run_shor():
    
    number = 15
    base = 2
    
    task_log = print
    
    print(f"SHOR number: {number}")
    
    if (number < 3 or 
        number % 2 == 0 or
        base < 2 or
        base >= number or
        math.gcd(base, number) != 1):
        
        raise ValueError("Incorrect input values")
    
    backend = Aer.get_backend('aer_simulator')
    
    quantum_instance = QuantumInstance(backend, shots=1024)
    
    shor = Shor()
    
    result = shor.factor(quantum_instance, number, base)
    
    print(f"SHOR Result: {result}")
    
    theoretical_qubits_count = 4 * math.ceil(math.log(number, 2)) + 2
    
    print(f'SHOR theoretical_qubits_count: {theoretical_qubits_count}')





import array
import fractions
import math
import sys
from typing import Optional, Union, List, Tuple

import numpy as np


from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister

from qiskit.circuit import Gate, Instruction, ParameterVector
from qiskit.circuit.library import QFT
from qiskit.utils.quantum_instance import QuantumInstance


class Shor:
    
    def factor(self, quantum_instance, number, base):

        result = set()
        circuit = self.create_shor_circuit(number=number, base=base)
        
        execution_job = quantum_instance.execute(circuit)
        counts = execution_job.get_counts(circuit)
        
        print(f"SHOR counts: {counts}")

        for measurement in counts:

            factors = self._get_factors(number, base, measurement)
            result |= set(factors or {})
            
            print(f"SHOR measurement: {measurement}")
            print(f"SHOR factors: {factors}")
        
        return result
        

    def create_shor_circuit(self, number, base):

        basic_qubit_count = number.bit_length()
        
        qft_qubits_count = basic_qubit_count * 2
        mult_qubits_count = basic_qubit_count
        ancilla_qubits_count = basic_qubit_count + 2
        measure_bits_count = basic_qubit_count * 2
        
        qft_register = QuantumRegister(qft_qubits_count, name="qft")
        mult_register = QuantumRegister(mult_qubits_count, name="mul")
        ancilla_register = QuantumRegister(ancilla_qubits_count, name="anc")
        measure_register = ClassicalRegister(measure_bits_count, name="mea")

        circuit = QuantumCircuit(qft_register, 
                                 mult_register, 
                                 ancilla_register,
                                 measure_register,
                                 name=f"Shor(N={number}, a={base})")

        circuit.h(qft_register)
        circuit.x(mult_register[0])

        modexp_circuit = self.create_modexp_circuit(number, base)
        circuit.append(modexp_circuit, circuit.qubits)

        iqft_circuit = QFT(qft_qubits_count).inverse().to_gate()
        circuit.append(iqft_circuit, qft_register)

        circuit.measure(qft_register, measure_register)

        print(f"SHOR circuit:\n{circuit}")

        return circuit        


    def create_modexp_circuit(self, number, base):
        
        basic_qubit_count = number.bit_length()
        
        qft_qubits_count = basic_qubit_count * 2
        mult_qubits_count = basic_qubit_count
        ancilla_qubits_count = basic_qubit_count + 2
        
        qft_register = QuantumRegister(qft_qubits_count, name="qft")
        mult_register = QuantumRegister(mult_qubits_count, name="mul")
        ancilla_register = QuantumRegister(ancilla_qubits_count, name="anc")

        modexp_circuit = QuantumCircuit(qft_register, 
                                        mult_register, 
                                        ancilla_register,
                                        name=f"{base}^x mod {number}")
                                 
        qft = QFT(basic_qubit_count + 1, do_swaps=False).to_gate()
        iqft = qft.inverse()
        
        phases = self.get_phases(number, basic_qubit_count + 1)

        phase_adder = self.create_phase_adder(phases)
        inverted_phase_adder = phase_adder.inverse()
        controlled_phase_adder = phase_adder.control(1)

        for i in range(2 * basic_qubit_count):
            
            partial_a = pow(base, 2**i, number)
            
            # print(f"SHOR i: {i}")
            # print(f"SHOR pow(base, 2**i): {pow(base, 2**i)}")
            # print(f"SHOR partial_a: {partial_a}")
            
            modulo_multiplier = self._controlled_multiple_mod_N(
                basic_qubit_count, 
                number, 
                partial_a,
                controlled_phase_adder, 
                inverted_phase_adder, 
                qft, 
                iqft
            )
            
            control_qubit = qft_register[i]
            
            modexp_qubits = [control_qubit, *mult_register, *ancilla_register]
            
            modexp_circuit.append(modulo_multiplier, modexp_qubits)
            
        print(f"SHOR modexp_circuit:\n{modexp_circuit}")
        
        return modexp_circuit.to_instruction()


    def create_phase_adder(self, phases):
        
        print(f"SHOR phases: {phases}")
        
        qubits_count = len(phases)
        
        phase_adder_circuit = QuantumCircuit(qubits_count, name="Phase adder")
        
        for i, phase in enumerate(phases):
            
            print(f"SHOR phase: {phase}")
            
            phase_adder_circuit.p(phase, i)
            
        print(f"SHOR phase_adder_circuit:\n{phase_adder_circuit}")
        
        return phase_adder_circuit.to_gate()
        

    def get_phases(self, a, n):
        """Calculates the array of angles to be used in the addition in Fourier Space."""
        bits_little_endian = (bin(int(a))[2:].zfill(n))[::-1]

        angles = np.zeros(n)
        for i in range(n):
            for j in range(i + 1):
                k = i - j
                if bits_little_endian[j] == "1":
                    angles[i] += pow(2, -k)
                    
        # print(f"SHOR angles {angles}")
        # print(f"SHOR angles * np.pi {angles * np.pi}")

        return angles * np.pi


    def _double_controlled_phi_add_mod_N(
        self,
        angles: Union[np.ndarray, ParameterVector],
        c_phi_add_N,
        iphi_add_N,
        qft,
        iqft,
    ):
        """Creates a circuit which implements double-controlled modular addition by a."""
        ctrl_qreg = QuantumRegister(2, "ctrl")
        b_qreg = QuantumRegister(len(angles), "b")
        flag_qreg = QuantumRegister(1, "flag")

        circuit = QuantumCircuit(ctrl_qreg, b_qreg, flag_qreg, name="ccphi_add_a_mod_N")

        cc_phi_add_a = self.create_phase_adder(angles).control(2)
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
            angles = self.get_phases(partial_constant, n + 1)
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
        
        # print(f"SHOR _controlled_multiple_mod_N circuit:\n{circuit}")   

        return circuit.to_instruction()
        

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
        print("In decimal, x_final value for this result is: %s.", x_final)

        if x_final <= 0:
            fail_reason = "x_final value is <= 0, there are no continued fractions."
        else:
            fail_reason = None
            print("Running continued fractions for this case.")

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
                print("Odd denominator, will try next iteration of continued fractions.")
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
                    print("Found just trivial factors, not good enough.")
                    # Check if the number has already been found,
                    # (use i - 1 because i was already incremented)
                    if t[i - 1] == 0:
                        fail_reason = "the continued fractions found exactly x_final/(2^(2n))."
                else:
                    # Successfully factorized N
                    return sorted((one_factor, other_factor))

        # Search for factors failed, write the reason for failure to the debug logs
        print(
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

        print("Approximation number %s of continued fractions:", len(b))
        print("Numerator:%s \t\t Denominator: %s.", frac.numerator, frac.denominator)
        return frac.denominator


run_shor()