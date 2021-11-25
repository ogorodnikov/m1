import math
import fractions
import numpy as np

from qiskit import Aer
from qiskit import execute

from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister

from qiskit.circuit import ParameterVector
from qiskit.circuit.library import QFT

try:
    from egcd import calculate_egcd
except ModuleNotFoundError:
    from core.algorithms.egcd import calculate_egcd


class Shor:
    
    def shor(self, run_values, task_log):
        
        run_values = {'number': '15', 'base': '2'}
        
        number_input = run_values.get('number')
        base_input = run_values.get('base')
        
        number = int(number_input)
        base = int(base_input)
        
        task_log(f'SHOR number: {number}')
        task_log(f'SHOR base: {base}')
        
        if (number < 3 or 
            number % 2 == 0 or
            base < 2 or
            base >= number or
            math.gcd(base, number) != 1):
            
            raise ValueError("Incorrect input values")
            
        circuit = self.create_shor_circuit(number=number, base=base)
        
        backend = Aer.get_backend('aer_simulator')
        
        job = execute(circuit, backend, shots=1024)
        
        counts = job.result().get_counts()        
        
        run_data = {'Result': {'Counts': counts}, 
                    'Run Values': {'number': number, 'base': base}}
        
        result = self.shor_post_processing(run_data=run_data, task_log=print)


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
        
        phases_count = basic_qubit_count + 1
        phases = self.get_phases(number, phases_count)

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
            
        # print(f"SHOR modexp_circuit:\n{modexp_circuit}")
        
        return modexp_circuit.to_instruction()


    def create_phase_adder(self, phases):
        
        qubits_count = len(phases)
        
        phase_adder_circuit = QuantumCircuit(qubits_count, name="Phase adder")
        
        for i, phase in enumerate(phases):
            phase_adder_circuit.p(phase, i)
            
        # print(f"SHOR phase_adder_circuit:\n{phase_adder_circuit}")
        
        return phase_adder_circuit.to_gate()
        

    def get_phases(self, number, phases_count):
        
        number_bits = bin(int(number))[2:]
        number_bits_filled = number_bits.zfill(phases_count)
        number_bits_reversed = reversed(number_bits_filled)
        digits = list(map(int, number_bits_reversed))
        
        # phases = [sum(math.pi * digit * 2 ** (j - i) for j, digit in enumerate(digits[:i + 1]))
        #               for i, _ in enumerate(digits)]

        angles = np.zeros(phases_count)
        
        for i in range(len(digits)):
            
            angle = 0
            
            for j, digit in enumerate(digits[:i + 1]):
                
                delta = j - i
                angle += digit * 2 ** delta
                
            angles[i] = angle
            
        phases = angles * np.pi

        # print(f"SHOR number: {number}")
        # print(f"SHOR digits: {digits}") 
        # print(f"SHOR phases {phases}")
        
        return phases
        
       
    def _controlled_multiple_mod_N(self, n, N, a, c_phi_add_N, iphi_add_N, qft, iqft):
        
        ctrl_qreg = QuantumRegister(1, "ctrl")
        x_qreg = QuantumRegister(n, "x")
        b_qreg = QuantumRegister(n + 1, "b")
        flag_qreg = QuantumRegister(1, "flag")

        circuit = QuantumCircuit(ctrl_qreg, x_qreg, b_qreg, flag_qreg, name="cmult_a_mod_N")
        
        angle_params = ParameterVector("angles", length=n + 1)
        
        modulo_adder = self._double_controlled_phi_add_mod_N(
            angle_params, c_phi_add_N, iphi_add_N, qft, iqft
        )

        def append_adder(adder, constant, idx):
            
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

        a_inv = self.modular_multiplicative_inverse(a, N)
        
        modulo_adder_inv = modulo_adder.inverse()
        
        for i in reversed(range(n)):
            append_adder(modulo_adder_inv, a_inv, i)

        circuit.append(iqft, b_qreg)
        
        # print(f"SHOR _controlled_multiple_mod_N circuit:\n{circuit}")
        
        return circuit.to_instruction()


    def _double_controlled_phi_add_mod_N(self, angles, c_phi_add_N, iphi_add_N, qft, iqft):
        
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
        
        # print(f"SHOR _double_controlled_phi_add_mod_N circuit:\n{circuit}")

        return circuit
        

    def modular_multiplicative_inverse(self, base, modulus):
        
        greatest_common_divisor, bezout_s, bezout_t = calculate_egcd(base, modulus)
        
        print(f"SHOR base, modulus: {base, modulus}")
        print(f'SHOR greatest_common_divisor: {greatest_common_divisor}')
        print(f'SHOR bezout_s: {bezout_s}')
        print(f'SHOR bezout_t: {bezout_t}') 
        
        if greatest_common_divisor != 1:
            
            raise ValueError(
                f"GCD of {base} and {modulus} is {greatest_common_divisor} - "
                f"modular inverse does not exist."
            )
                
        return bezout_s % modulus

    
    def shor_post_processing(self, run_data, task_log):
    
        number_str = run_data['Run Values']['number']
        base_str = run_data['Run Values']['base']
        counts = run_data['Result']['Counts']
        
        number = int(number_str)
        base = int(base_str)
        
        states = list(counts)
        qubits_count = len(states[0])
    
        task_log(f'SHOR run_data: {run_data}')
    
        task_log(f'SHOR number: {number}')
        task_log(f'SHOR base: {base}')
        task_log(f'SHOR counts: {counts}')
        
        task_log(f'SHOR states: {states}')
        task_log(f'SHOR qubits_count: {qubits_count}')
        
        orders = []
        
        for state in states:
            
            state_binary = int(state, 2)
            
            phase = state_binary / 2 ** qubits_count
            
            phase_fraction = fractions.Fraction(phase).limit_denominator(15)
            
            order = phase_fraction.denominator
            
            orders.append(order)
            
            task_log(f'SHOR state: {state}')
            task_log(f'SHOR state_binary: {state_binary}')
            task_log(f'SHOR phase: {phase}')
            task_log(f'SHOR phase_fraction: {phase_fraction}')
            task_log(f'SHOR order: {order}')
        
        filtered_orders = list(filter(lambda order: order % 2 == 0, orders))
    
        factors = set()
        
        for order in filtered_orders:
            
            factor_p_1 = math.gcd(base ** (order // 2) - 1, number)
            factor_p_2 = math.gcd(base ** (order // 2) + 1, number)
            
            factor_q_1 = number // factor_p_1
            factor_q_2 = number // factor_p_2
            
            task_log(f'SHOR factor_p_1: {factor_p_1}')
            task_log(f'SHOR factor_p_2: {factor_p_2}')
            
            task_log(f'SHOR factor_q_1: {factor_q_1}')
            task_log(f'SHOR factor_q_2: {factor_q_2}')
            
            factors.add(factor_p_1)
            factors.add(factor_p_2)
            factors.add(factor_q_1)
            factors.add(factor_q_2)

        non_trivial_factors = list(factors - {1, number})

        task_log(f'SHOR orders: {orders}')   
        task_log(f'SHOR filtered_orders: {filtered_orders}')
        task_log(f'SHOR factors: {factors}')    
        task_log(f'SHOR non_trivial_factors: {non_trivial_factors}')
        
        return {'Factors': non_trivial_factors}
        

def shor(run_values, task_log):
    Shor().shor(run_values, task_log)
    
shor_post_processing = Shor().shor_post_processing
