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
    

    # QPE Circuit
    
    counting_qubits_count = precision
    counting_qubits = range(counting_qubits_count)
    
    estimation_register = QuantumRegister(precision, 'estimation')
    eigenstate_register = QuantumRegister(1, 'eigenstate')
    
    eigenstate_qubit = max(counting_qubits) + 1
    qubits_count = counting_qubits_count + 1
    
    qpe_circuit = QuantumCircuit(estimation_register, eigenstate_register)
    qpe_circuit.name = 'QPE'
    
    qpe_circuit.h(estimation_register)
    
    # QPE Iterations
    
    for estimation_qubit_index, estimation_qubit in enumerate(estimation_register):
    
        iterations_count = 2 ** estimation_qubit_index
        
        for iteration in range(iterations_count):
        
            iteration_qubits = [estimation_qubit, *eigenstate_register]
            
            qpe_circuit.append(controlled_bernoulli_diffuser, iteration_qubits)
    
    # IQFT
    
    iqft_circuit = create_qft_circuit(precision, inverted=True)
    
    qpe_circuit.append(iqft_circuit, estimation_register)
    
    
    # QAE Circuit

    measure_register = ClassicalRegister(precision)
    
    qae_circuit = QuantumCircuit(estimation_register, eigenstate_register, measure_register)
    
    qae_circuit.append(bernoulli_operator, [eigenstate_qubit])
    qae_circuit.append(qpe_circuit, [*counting_qubits, eigenstate_qubit])

    qae_circuit.measure(estimation_register, measure_register)
    

    # Logs
    
    task_log(f'QAE run_values: {run_values}')
    
    task_log(f'QAE bernoulli_probability: {bernoulli_probability}')
    task_log(f'QAE precision: {precision}')
    
    task_log(f'QAE theta_p: {theta_p}')
    
    task_log(f'QAE bernoulli_operator:\n{bernoulli_operator}')
    task_log(f'QAE bernoulli_diffuser:\n{bernoulli_diffuser}')
    
    task_log(f'QAE iqft_circuit: \n{iqft_circuit}')
    task_log(f'QAE qpe_circuit: \n{qpe_circuit}')
    task_log(f'QAE qae_circuit:\n{qae_circuit}')
    
    
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