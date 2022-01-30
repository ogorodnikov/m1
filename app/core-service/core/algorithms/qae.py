from math import pi, sin, asin

from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister

try:
    from qft import create_qft_circuit
except ModuleNotFoundError:
    from core.algorithms.qft import create_qft_circuit
    

AMPLITUDE_DIGITS_COUNT = 7
    


def qae(run_values, task_log):
    
    ''' https://qiskit.org/documentation/finance/tutorials/00_amplitude_estimation.html '''
    
    # Input
    
    input_probability = run_values.get('bernoulli_probability')
    input_precision = run_values.get('precision')
    
    probability = float(input_probability)
    precision = int(input_precision)
    
    # Circuits
    
    bernoulli_a = QuantumCircuit(1)
    bernoulli_q = QuantumCircuit(1)
    
    theta_p = 2 * asin(probability ** 0.5)
    
    bernoulli_a.ry(theta_p, 0)
    bernoulli_q.ry(2 * theta_p, 0)
    
    # QPE
    
    counting_qubits_count = precision
    counting_qubits = range(counting_qubits_count)
    
    # node_register = QuantumRegister(4, 'node')
    
    eigenstate_qubit = max(counting_qubits) + 1
    qubits_count = counting_qubits_count + 1
    
    measure_bits_count = counting_qubits_count
    measure_bits = range(measure_bits_count)
    
    qubits_measurement_list = list(reversed(counting_qubits))

    qpe_circuit = QuantumCircuit(qubits_count)
    qpe_circuit.name = 'QPE'
    
    for counting_qubit in counting_qubits:
        qpe_circuit.h(counting_qubit)
        
    controlled_bernoulli_q = bernoulli_q.control()
    controlled_bernoulli_q.name = 'CB'
    
    
    for repetitions, counting_qubit in enumerate(counting_qubits):
        
        for i in range(2 ** repetitions):
        
            iteration_qubits = [counting_qubit, eigenstate_qubit]
            
            qpe_circuit.append(controlled_bernoulli_q, iteration_qubits)
    
    # IQFT
    
    iqft_circuit = create_qft_circuit(counting_qubits_count, inverted=True)
    
    qpe_circuit.append(iqft_circuit, counting_qubits)
    
    # qpe_circuit.barrier()
    
    # qpe_circuit.measure(qubits_measurement_list, measure_bits)
    
    task_log(f'QAE iqft_circuit: \n{iqft_circuit}')
    task_log(f'QAE qpe_circuit: \n{qpe_circuit}')


    counting_register = QuantumRegister(counting_qubits_count)
    eigenstate_register = QuantumRegister(1)

    measure_register = ClassicalRegister(counting_qubits_count)
    
    qae_circuit = QuantumCircuit(counting_register, eigenstate_register, measure_register)
    
    qae_circuit.append(bernoulli_a, [eigenstate_qubit])
    qae_circuit.append(qpe_circuit, [*counting_qubits, eigenstate_qubit])

    # Measure
    
    qae_circuit.measure(counting_register, measure_register)
    
    
    task_log(f'QAE qae_circuit:\n{qae_circuit}')

    # Logs
    
    task_log(f'QAE run_values: {run_values}')
    
    task_log(f'QAE probability: {probability}')
    
    task_log(f'QAE theta_p: {theta_p}')
    
    task_log(f'QAE bernoulli_a:\n{bernoulli_a}')
    task_log(f'QAE bernoulli_q:\n{bernoulli_q}')
    
    task_log(f'QAE qae_circuit: {qae_circuit}')
    
    return qae_circuit




def qae_post_processing(run_data, task_log):
    
    # Inputs
    
    run_result = run_data.get('Result')
    counts = run_result.get('Counts')
    
    # Precision
    
    first_state = next(iter(counts))
    precision = len(first_state)
    
    qubits_count = precision
    

    # Amplitude probabilities
    
    counts_total = sum(counts.values())
    
    state_probabilities = dict()
    amplitude_probabilities = dict()
    
    for state_binary, count in counts.items():
        
        reversed_state = state_binary[::-1]
        state_decimal = int(reversed_state, 2)
        
        # State probability
    
        state_probability = count / counts_total
        state_probabilities[state_decimal] = state_probability
        
        # Amplitude
        
        amplitude = sin(state_decimal * pi / 2 ** qubits_count) ** 2
        rounded_amplitude = round(amplitude, ndigits=AMPLITUDE_DIGITS_COUNT)
        
        amplitude_probability = amplitude_probabilities.get(rounded_amplitude, 0.0)
        
        amplitude_probabilities[rounded_amplitude] = amplitude_probability + state_probability
        
    
    # Estimation
    
    estimated_amplitude, estimated_amplitude_probability = max(amplitude_probabilities.items(), 
                                                               key=lambda item: item[1])
    
    # Printouts
    
    task_log(f'QAE qae_post_processing')
    
    # task_log(f'QAE circuit:\n{circuit}')
    # task_log(f'QAE counts: {counts}')
    
    task_log(f'QAE state_probabilities: {state_probabilities}')
    task_log(f'QAE amplitude_probabilities: {amplitude_probabilities}')
    
    task_log(f'QAE estimated_amplitude: {estimated_amplitude}')
    task_log(f'QAE estimated_amplitude_probability: {estimated_amplitude_probability}')
    

    return {'Amplitude': estimated_amplitude}