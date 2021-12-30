from math import pi
from math import sin

from qiskit import QuantumCircuit

# try:
#     from grover import build_phase_oracle
#     from grover import build_diffuser
# except ModuleNotFoundError:
#     from core.algorithms.grover import build_phase_oracle
    # from core.algorithms.grover import build_diffuser

try:
    from qft import create_qft_circuit
except ModuleNotFoundError:
    from core.algorithms.qft import create_qft_circuit
    
    
def example_grover_iteration(qubits_count, secrets):

    circuit = QuantumCircuit(4)
    
    # Oracle
    circuit.h([2,3])
    circuit.ccx(0,1,2)
    circuit.h(2)
    circuit.x(2)
    circuit.ccx(0,2,3)
    circuit.x(2)
    circuit.h(3)
    circuit.x([1,3])
    circuit.h(2)
    circuit.mct([0,1,3],2)
    circuit.x([1,3])
    circuit.h(2)
    
    # circuit.barrier()
    
    # Diffuser
    circuit.h(range(3))
    circuit.x(range(3))
    circuit.z(3)
    circuit.mct([0,1,2],3)
    circuit.x(range(3))
    circuit.h(range(3))
    circuit.z(3)
    
    return circuit


def build_diffuser(qubits_count, flipped=False):
    
    qubits = range(qubits_count)
    
    circuit = QuantumCircuit(qubits_count)
    
    for qubit in range(qubits_count):
        circuit.h(qubit)

    for qubit in range(qubits_count):
        circuit.x(qubit)
        
    for qubit in range(1, qubits_count):
        circuit.i(qubit)

    circuit.h(0)
    circuit.mct(list(range(1, qubits_count)), 0)
    circuit.h(0)
    
    for qubit in range(1, qubits_count):
        circuit.i(qubit)

    for qubit in range(qubits_count):
        circuit.x(qubit)

    for qubit in range(qubits_count):
        circuit.h(qubit)
        
    return circuit
        

def grover_iteration(qubits_count, secrets):

    qubits_count = 4
    qubits = range(qubits_count)

    circuit = QuantumCircuit(qubits_count)
    
    # # Oracle
    # circuit.h([2,3])
    # circuit.ccx(0,1,2)
    # circuit.h(2)
    # circuit.x(2)
    # circuit.ccx(0,2,3)
    # circuit.x(2)
    # circuit.h(3)
    # circuit.x([1,3])
    # circuit.h(2)
    # circuit.mct([0,1,3],2)
    # circuit.x([1,3])
    # circuit.h(2)
    
    # circuit.barrier()
    
    # Diffuser
    circuit.h(range(3))
    circuit.x(range(3))
    circuit.z(3)
    circuit.mct([0,1,2],3)
    circuit.x(range(3))
    circuit.h(range(3))
    circuit.z(3)
    
    
    diffuser = build_diffuser(qubits_count=qubits_count)
    
    print(f'COUNT circuit:\n{circuit}')
    
    print(f'COUNT diffuser:\n{diffuser}')
    
    quit()
    

        

 
    
    return circuit
    
    
def quantum_counting(run_values, task_log):
    
    secrets = [value for key, value in run_values.items() if 'secret' in key]
    secret_count = len(secrets)
    
    qubits_count = len(max(secrets, key=len))
    
    
    # CGRIT
    
    # grover_iteration_circuit = example_grover_iteration(qubits_count, secrets)
    
    grover_iteration_circuit = grover_iteration(qubits_count, secrets)
    
    grover_iteration_gate = grover_iteration_circuit.to_gate()
    controlled_grover_iteration = grover_iteration_gate.control()
    
    grover_iteration_gate.label = "Grover Iteration Gate"
    
    
    # Circuit
    
    counting_qubits_count = 4
    searching_qubits_count = 4
    total_qubits_count = counting_qubits_count + searching_qubits_count
    
    counting_qubits = list(range(counting_qubits_count))
    searching_qubits = list(range(counting_qubits_count, total_qubits_count))
    all_qubits = list(range(total_qubits_count))
    
    measurement_bits_count = counting_qubits_count
    measurement_bits = list(range(measurement_bits_count))
    
    circuit = QuantumCircuit(total_qubits_count, measurement_bits_count)
    
    circuit.h(all_qubits)
    
    
    # Apply CGRITs
    
    for counting_qubit in counting_qubits:
        
        iterations_count = 2 ** counting_qubit
        
        for iteration in range(iterations_count):
            
            task_log(f'COUNT iteration: {iteration}')
            
            iteration_qubits = [counting_qubit] + searching_qubits
            
            circuit.append(controlled_grover_iteration, iteration_qubits)
    
    # IQFT
    
    iqft_circuit = create_qft_circuit(4, inverted=True)
    
    circuit.append(iqft_circuit, counting_qubits)
    
    
    # Measure
    
    circuit.measure(list(reversed(counting_qubits)), measurement_bits)
    
    
    task_log(f'COUNT run_values: {run_values}')
    
    task_log(f'COUNT grover_iteration_circuit:\n{grover_iteration_circuit}')
    task_log(f'COUNT grover_iteration_gate:\n{grover_iteration_gate}')
    task_log(f'COUNT controlled_grover_iteration:\n{controlled_grover_iteration}')
    
    task_log(f'COUNT iqft_circuit:\n{iqft_circuit}')
    
    task_log(f'COUNT circuit:\n{circuit}')
    
    task_log(f'COUNT counting_qubits:\n{counting_qubits}')
    task_log(f'COUNT searching_qubits:\n{searching_qubits}')
    task_log(f'COUNT all_qubits:\n{all_qubits}')
    task_log(f'COUNT measurement_bits:\n{measurement_bits}')
    
    
    return circuit
    
    
def quantum_counting_post_processing(run_data, task_log):
    
    run_values = run_data['Run Values']
    counts = run_data['Result']['Counts']
    
    max_secret_len = max(map(len, run_values.values()))
    
    counting_qubits_count = max_secret_len
    searching_qubits_count = max_secret_len
    
    most_probable_result = max(counts, key=counts.get)
    
    most_probable_result_int = int(most_probable_result, 2)
    
    qpe_phi = most_probable_result_int / 2 ** counting_qubits_count
    theta = qpe_phi * 2 * pi
    
    total_states_count = 2 ** searching_qubits_count
    non_solutions_count = total_states_count * sin(theta / 2) ** 2
    
    solutions_count = total_states_count - non_solutions_count
    
    error_upper_bound = counting_qubits_count - 1
    
    error = (((2 * solutions_count * total_states_count) ** 0.5 +
              total_states_count / 2 ** (error_upper_bound + 1)) * 
             2 ** -error_upper_bound)
    
    
    task_log(f'COUNT quantum_counting_post_processing')
    
    task_log(f'COUNT run_data: {run_data}')
    task_log(f'COUNT run_values: {run_values}')
    task_log(f'COUNT counts: {counts}')
    
    task_log(f'COUNT counting_qubits_count: {counting_qubits_count}')
    
    task_log(f'COUNT most_probable_result: {most_probable_result}')
    task_log(f'COUNT most_probable_result_int: {most_probable_result_int}')
    
    task_log(f'COUNT qpe_phi: {qpe_phi}')
    task_log(f'COUNT theta: {theta}')
    
    task_log(f'COUNT total_states_count: {total_states_count}')
    task_log(f'COUNT non_solutions_count: {non_solutions_count}')
    task_log(f'COUNT solutions_count: {solutions_count}')
    
    task_log(f'COUNT error_upper_bound: {error_upper_bound}')
    task_log(f'COUNT error: {error}')
