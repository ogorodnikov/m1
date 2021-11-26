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
    
    def run_shor(self, run_values, task_log):
        
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

        # modexp_circuit = self.create_modexp_circuit(number, base)
        # circuit.append(modexp_circuit, circuit.qubits)


    # def create_modexp_circuit(self, number, base):
        
    #     basic_qubit_count = number.bit_length()
        
    #     qft_qubits_count = basic_qubit_count * 2
    #     mult_qubits_count = basic_qubit_count
    #     ancilla_qubits_count = basic_qubit_count + 2
        
    #     qft_register = QuantumRegister(qft_qubits_count, name="qft")
    #     mult_register = QuantumRegister(mult_qubits_count, name="mul")
    #     ancilla_register = QuantumRegister(ancilla_qubits_count, name="anc")

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
            
            partial_base = pow(base, 2**i, number)
            
            # print(f"SHOR i: {i}")
            # print(f"SHOR number: {number}")
            # print(f"SHOR partial_base = pow(base, 2**i, number): {pow(base, 2**i, number)}")
            
            controlled_modular_multiplier = self.controlled_modular_multiplier(
                basic_qubit_count, 
                number, 
                partial_base,
                controlled_phase_adder, 
                inverted_phase_adder, 
                qft, 
                iqft
            )
            
            control_qubit = qft_register[i]
            
            modexp_qubits = [control_qubit, *mult_register, *ancilla_register]
            
            # modexp_circuit.append(controlled_modular_multiplier, modexp_qubits)
            
            circuit.append(controlled_modular_multiplier, modexp_qubits)
            
            
        
        final_iqft_circuit = QFT(qft_qubits_count).inverse().to_gate()
        circuit.append(final_iqft_circuit, qft_register)

        circuit.measure(qft_register, measure_register)

        print(f"SHOR circuit:\n{circuit}")
        
        # quit()
        
        return circuit 
        
        
            
        # print(f"SHOR modexp_circuit:\n{modexp_circuit}")
        
        # quit()
        
        # return modexp_circuit.to_instruction()
        
       
    def controlled_modular_multiplier(
            self, 
            basic_qubit_count, 
            number, 
            base, 
            controlled_phase_adder, inverted_phase_adder, qft, iqft):
        
        control_register = QuantumRegister(1, "ctrl")
        x_qreg = QuantumRegister(basic_qubit_count, "x")
        b_qreg = QuantumRegister(basic_qubit_count + 1, "b")
        flag_register = QuantumRegister(1, "flag")
        

        circuit = QuantumCircuit(
            control_register, x_qreg, b_qreg, flag_register, 
            name="Controlled Modular Multiplier")
        
        phase_parameters = ParameterVector("phases", length=basic_qubit_count + 1)
        
        double_controlled_modular_adder = self.double_controlled_modular_adder(
            phase_parameters, controlled_phase_adder, inverted_phase_adder, qft, iqft
        )

        def append_adder(adder, constant, idx):
            
            partial_constant = (pow(2, idx, number) * constant) % number
            
            phases = self.get_phases(partial_constant, basic_qubit_count + 1)
            
            bound = adder.assign_parameters({phase_parameters: phases})
            
            adder_qubits = [*control_register, x_qreg[idx], *b_qreg, *flag_register]
            
            circuit.append(bound, adder_qubits)
            

        circuit.append(qft, b_qreg)
        

        for i in range(basic_qubit_count):
            append_adder(double_controlled_modular_adder, base, i)

        circuit.append(iqft, b_qreg)
        

        for i in range(basic_qubit_count):
            circuit.cswap(control_register, x_qreg[i], b_qreg[i])

        circuit.append(qft, b_qreg)

        base_inverse = self.modular_multiplicative_inverse(base=base, modulus=number)
        
        double_controlled_modular_adder_inverse = double_controlled_modular_adder.inverse()
        
        for i in reversed(range(basic_qubit_count)):
            append_adder(double_controlled_modular_adder_inverse, base_inverse, i)

        circuit.append(iqft, b_qreg)
        
        # print(f"SHOR controlled_modular_multiplier:\n{circuit}")
        
        return circuit.to_instruction()


    def double_controlled_modular_adder(self, 
                                        phase_parameters, 
                                        controlled_phase_adder, 
                                        inverted_phase_adder, 
                                        qft, iqft):
        
        control_register = QuantumRegister(1, "ctrl")
        mult_register = QuantumRegister(1, "mult")
        add_register = QuantumRegister(len(phase_parameters), "add")
        comparison_register = QuantumRegister(1, "comp")
        
        circuit = QuantumCircuit(
            control_register, 
            mult_register, 
            add_register, 
            comparison_register,
            name="Double Controlled Modular Adder"
        )

        adder_with_parameters = self.create_phase_adder(phase_parameters)
        double_controlled_adder = adder_with_parameters.control(2)
        
        inverted_double_controlled_adder = double_controlled_adder.inverse()
        
        
        # compute modular addition

        circuit.append(double_controlled_adder, [*control_register, 
                                                 *mult_register, 
                                                 *add_register])

        circuit.append(inverted_phase_adder, add_register)
        circuit.append(iqft, add_register)
        
        circuit.cx(add_register[-1], comparison_register[0])
        
        circuit.append(qft, add_register)
        circuit.append(controlled_phase_adder, [*comparison_register, 
                                                *add_register])
        
        # uncompute modular addition

        circuit.append(inverted_double_controlled_adder, [*control_register, 
                                                          *mult_register, 
                                                          *add_register])
        circuit.append(iqft, add_register)
        
        circuit.x(add_register[-1])
        circuit.cx(add_register[-1], comparison_register[0])
        circuit.x(add_register[-1])
        
        circuit.append(qft, add_register)
        circuit.append(double_controlled_adder, [*control_register, 
                                                 *mult_register, 
                                                 *add_register])
        
        # print(f"SHOR double_controlled_modular_adder:\n{circuit}")
        
        return circuit
        

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
        

    def modular_multiplicative_inverse(self, base, modulus):
        
        greatest_common_divisor, bezout_s, bezout_t = calculate_egcd(base, modulus)
        
        if greatest_common_divisor != 1:
            raise ValueError(f"Modular inverse does not exist")
                
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
            
            task_log()
            task_log(f'SHOR state: {state}')
            task_log(f'SHOR state_binary: {state_binary}')
            task_log(f'SHOR phase: {phase}')
            task_log(f'SHOR phase_fraction: {phase_fraction}')
            task_log(f'SHOR order: {order}')
        
        factors = set()
        
        for order in orders:
            
            factor_p1 = math.gcd(base ** (order // 2) - 1, number)
            factor_p2 = math.gcd(base ** (order // 2) + 1, number)
            
            factor_q1 = number // factor_p1
            factor_q2 = number // factor_p2
            
            # task_log(f'SHOR factor_p1: {factor_p1}')
            # task_log(f'SHOR factor_p2: {factor_p2}')
            # task_log(f'SHOR factor_q1: {factor_q1}')
            # task_log(f'SHOR factor_q2: {factor_q2}')
            
            factors.add(factor_p1)
            factors.add(factor_p2)
            factors.add(factor_q1)
            factors.add(factor_q2)

        non_trivial_factors = factors - {1, number}
        
        task_log()
        task_log(f'SHOR orders: {orders}')   
        task_log(f'SHOR factors: {factors}')    
        task_log(f'SHOR non_trivial_factors: {non_trivial_factors}')
        
        return {'Factors': non_trivial_factors}


run_values = {'number': '15', 'base': '2'}

Shor().run_shor(run_values, print)
