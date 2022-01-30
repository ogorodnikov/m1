from math import pi, sin, asin

from qiskit import QuantumCircuit

AMPLITUDE_DIGITS_COUNT = 7
    


def qae(run_values, task_log):
    
    ''' https://qiskit.org/documentation/finance/tutorials/00_amplitude_estimation.html '''
    
    # Input
    
    input_probability = run_values.get('bernoulli_probability')
    probability = float(input_probability)
    
    
    # Circuits
    
    bernoulli_a = QuantumCircuit(1)
    bernoulli_q = QuantumCircuit(1)
    
    theta_p = 2 * asin(probability ** 0.5)
    
    bernoulli_a.ry(theta_p, 0)
    bernoulli_q.ry(2 * theta_p, 0)
    
    
    # Reference Estimation
    
    class Task:
        
        def __init__(self):
            
            self.state_preparation = bernoulli_a
            self.grover_operator = bernoulli_q
            self.objective_qubits = [0]
            self.post_processing = lambda x: x
            
    task = Task()        
            
    
    
    from qiskit import Aer
    from qiskit import BasicAer
    from qiskit.utils import QuantumInstance
    
    # backend = BasicAer.get_backend("statevector_simulator")
    backend = Aer.get_backend("aer_simulator")
    quantum_instance = QuantumInstance(backend)
    
    
    from amplitude_estimation import AmplitudeEstimation

    ae = AmplitudeEstimation(
        num_eval_qubits=5,
        quantum_instance=quantum_instance
    )
    
    ae_result = ae.estimate(task)
    
    estimation = ae_result.estimation
    samples = ae_result.samples
    
    measurements = ae_result.measurements
    
    max_probability = ae_result.max_probability 
    estimation = ae_result.estimation
    estimation_processed = ae_result.estimation_processed
    
    
    # Custom Circuit
    
    num_eval_qubits = 5
    state_preparation = bernoulli_a
    iqft = None
    
    from qiskit import ClassicalRegister
    from qiskit.circuit.library import PhaseEstimation

    pec = PhaseEstimation(num_eval_qubits, bernoulli_q, iqft=iqft)
    
    task_log(f'QAE pec: {pec.decompose()}')

    
    # Custom QPE
    
    counting_qubits_count = num_eval_qubits
    counting_qubits = range(counting_qubits_count)
    
    # node_register = QuantumRegister(4, 'node')
    
    eigenstate_qubit = max(counting_qubits) + 1
    qubits_count = counting_qubits_count + 1
    
    measure_bits_count = counting_qubits_count
    measure_bits = range(measure_bits_count)
    
    qubits_measurement_list = list(reversed(counting_qubits))

    phase_estimation_circuit = QuantumCircuit(qubits_count, measure_bits_count)
    phase_estimation_circuit.name = 'Cust QPE'
    
    for counting_qubit in counting_qubits:
        phase_estimation_circuit.h(counting_qubit)
        
    # phase_estimation_circuit.x(eigenstate_qubit)
    
    controlled_bernoulli_q = bernoulli_q.control()
    controlled_bernoulli_q.name = 'CB'
    
    
    for repetitions, counting_qubit in enumerate(counting_qubits):
        
        for i in range(2 ** repetitions):
        
            # circuit.cp(pi * angle_number, counting_qubit, eigenstate_qubit)
            
            iteration_qubits = [counting_qubit, eigenstate_qubit]
            
            phase_estimation_circuit.append(controlled_bernoulli_q, iteration_qubits)
    
    task_log(f'QAE phase_estimation_circuit: \n{phase_estimation_circuit}')
    
    quit()
    
            
    qft_dagger_circuit = create_qft_circuit(counting_qubits_count, inverted=True)
    
    circuit.append(qft_dagger_circuit, counting_qubits)
    
    circuit.barrier()
    
    circuit.measure(qubits_measurement_list, measure_bits)
    
    
    task_log(f'QAE angle: \n{angle}')
    task_log(f'QAE precision: \n{precision}')
    
    task_log(f'QAE qft_dagger_circuit: \n{qft_dagger_circuit}')
    task_log(f'QAE circuit: \n{circuit}')

    quit()
    
    


    circuit = QuantumCircuit(*pec.qregs)
    
    circuit.compose(
        state_preparation,
        list(range(num_eval_qubits, circuit.num_qubits)),
        inplace=True,
    )
    circuit.compose(pec, inplace=True)

    # Measurements
    
    cr = ClassicalRegister(num_eval_qubits)
    circuit.add_register(cr)
    circuit.measure(list(range(num_eval_qubits)), list(range(num_eval_qubits)))


    # Logs
    
    task_log(f'QAE run_values: {run_values}')
    
    task_log(f'QAE probability: {probability}')
    
    task_log(f'QAE theta_p: {theta_p}')
    
    task_log(f'QAE bernoulli_a:\n{bernoulli_a}')
    task_log(f'QAE bernoulli_q:\n{bernoulli_q}')
    
    task_log(f'QAE circuit: {circuit}')
    
    task_log(f'')
    task_log(f'QAE samples: {samples}')
    task_log(f'QAE measurements: {measurements}')
    task_log(f'QAE max_probability: {max_probability}')
    task_log(f'QAE estimation: {estimation}')
    task_log(f'QAE estimation_processed: {estimation_processed}')
    
    return circuit




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