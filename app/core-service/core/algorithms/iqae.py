from math import pi, sin, asin

from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister

try:
    from qft import create_qft_circuit
except ModuleNotFoundError:
    from core.algorithms.qft import create_qft_circuit

AMPLITUDE_DIGITS_COUNT = 7


def iqae(run_values, task_log):
    
    """
    Create Iterative Quantum Amplitude Estimation (IQAE) circuit
    
    https://qiskit.org/documentation/finance/tutorials/00_amplitude_estimation.html
    
    """
    
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
    controlled_bernoulli_diffuser.name = 'Controlled Bernoulli Diffuser'
    
    bernoulli_operator.name = 'Bernoulli Operator'
    bernoulli_diffuser.name = 'Bernoulli Diffuser'
    controlled_bernoulli_diffuser.name = 'CBD'
    
    
    # Reference IQAE
    
    from qiskit.algorithms import EstimationProblem

    problem = EstimationProblem(
        state_preparation=bernoulli_operator,
        grover_operator=bernoulli_diffuser,
        objective_qubits=[0],
    )


    
    from qiskit import Aer
    from qiskit.utils import QuantumInstance
    
    backend = Aer.get_backend("aer_simulator")
    quantum_instance = QuantumInstance(backend)


    
    from iqae_reference import IterativeAmplitudeEstimation
    
    accuracy = 0.01
    width_of_cofidence_interval = 0.05

    iae = IterativeAmplitudeEstimation(
        epsilon_target=accuracy,
        alpha=width_of_cofidence_interval,
        quantum_instance=quantum_instance,
    )
    iae_result = iae.estimate(problem)
    
    print("Estimate:", iae_result.estimation)
    
    iae_circuit = iae.construct_circuit(problem, k=3)
    iae_circuit.draw("mpl", style="iqx")
    
    
    quit()
    

    # QPE Circuit
    
    estimation_register = QuantumRegister(precision, 'estimation')
    eigenstate_register = QuantumRegister(1, 'eigenstate')
    
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

    measure_register = ClassicalRegister(precision, 'measurement')
    
    qae_circuit = QuantumCircuit(estimation_register, 
                                 eigenstate_register, 
                                 measure_register)
    
    qae_circuit.append(bernoulli_operator, eigenstate_register)
    qae_circuit.append(qpe_circuit, [*estimation_register,
                                     *eigenstate_register])

    qae_circuit.measure(estimation_register, measure_register)
    

    # Logs
    
    task_log(f'QAE run_values: {run_values}\n')
    
    task_log(f'QAE bernoulli_probability: {bernoulli_probability}')
    task_log(f'QAE precision: {precision}\n')
    
    task_log(f'QAE theta_p: {theta_p}\n')
    
    task_log(f'QAE bernoulli_operator:\n{bernoulli_operator}\n')
    task_log(f'QAE bernoulli_diffuser:\n{bernoulli_diffuser}\n')
    
    task_log(f'QAE iqft_circuit: \n{iqft_circuit}\n')
    task_log(f'QAE qpe_circuit: \n{qpe_circuit}\n')
    task_log(f'QAE qae_circuit:\n{qae_circuit}\n')
    
    return qae_circuit
