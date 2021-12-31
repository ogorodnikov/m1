from qiskit import QuantumCircuit


def bb84(run_values, task_log):
    
    
    # Alice side
    
    alice_bits = '1010'
    
    alice_bases = 'XZXX'
    
    qubits = []
    
    for bit, base in zip(alice_bits, alice_bases):
        
        qubit = QuantumCircuit(1, 1)
        
        if bit == '1':
            qubit.x(0)
            
        if base == 'X':
            qubit.h(0)
            
        qubit.barrier()
        
        qubits.append(qubit)
        
    
        
    
    # Logs
    
    task_log(f'BB84 run_values: {run_values}')