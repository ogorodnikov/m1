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
    
    from qiskit.algorithms import EstimationProblem

    problem = EstimationProblem(
        state_preparation=bernoulli_a,
        grover_operator=bernoulli_q,
        objective_qubits=[0]
    )
    
    
    from qiskit import BasicAer
    from qiskit.utils import QuantumInstance
    
    backend = BasicAer.get_backend("statevector_simulator")
    quantum_instance = QuantumInstance(backend)
    
    
    from qiskit.algorithms import AmplitudeEstimation

    ae = AmplitudeEstimation(
        num_eval_qubits=3,
        quantum_instance=quantum_instance
    )
    
    ae_result = ae.estimate(problem)
    
    result = ae_result.estimation
    samples = ae_result.samples
    
    # Logs
    
    task_log(f'QAE run_values: {run_values}')
    
    task_log(f'QAE probability: {probability}')
    
    task_log(f'QAE theta_p: {theta_p}')
    
    task_log(f'QAE bernoulli_a:\n{bernoulli_a}')
    task_log(f'QAE bernoulli_q:\n{bernoulli_q}')
    
    task_log(f'QAE result: {result}')
    task_log(f'QAE samples: {samples}')