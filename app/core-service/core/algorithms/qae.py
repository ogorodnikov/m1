from math import asin

from qiskit import QuantumCircuit


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
            
    
    
    from qiskit import BasicAer
    from qiskit.utils import QuantumInstance
    
    backend = BasicAer.get_backend("statevector_simulator")
    quantum_instance = QuantumInstance(backend)
    
    
    from amplitude_estimation import AmplitudeEstimation

    ae = AmplitudeEstimation(
        num_eval_qubits=5,
        quantum_instance=quantum_instance
    )
    
    ae_result = ae.estimate(task)
    
    simple_result = ae_result.estimation
    samples = ae_result.samples
    
    
    
    # Circuit
    
    num_eval_qubits = 5
    state_preparation = bernoulli_a
    iqft = None
    
    from qiskit import ClassicalRegister
    from qiskit.circuit.library import PhaseEstimation

    pec = PhaseEstimation(num_eval_qubits, bernoulli_q, iqft=iqft)


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
    
    task_log(f'QAE simple_result: {simple_result}')
    task_log(f'QAE samples: {samples}')
    
    task_log(f'QAE circuit: {circuit}')
    
    return circuit
