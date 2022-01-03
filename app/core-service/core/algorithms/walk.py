from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister


def walk(run_values, task_log):
    
    
    # Registers
    
    theta_register = QuantumRegister(4, 'theta')
    node_register = QuantumRegister(4, 'node')
    coin_register = QuantumRegister(4, 'coin')
    auxilary_register = QuantumRegister(4, 'auxilary')
    
    measure_register = ClassicalRegister(4, 'measure')
    
    circuit = QuantumCircuit(theta_register,
                             node_register,
                             coin_register,
                             auxilary_register,
                             measure_register)
                             
    circuit.h(node_register)
    circuit.h(coin_register)
    
    # Logs
    
    task_log(f'WALK run_values: {run_values}')