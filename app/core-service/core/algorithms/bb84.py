from qiskit import QuantumCircuit

from qiskit import Aer, assemble




def bb84(run_values, task_log):
    
    
    # Alice side
    
    alice_bits = '1010'
    
    alice_bases = 'XZXX'
    
    qubits = []
    
    for alice_bit, alice_base in zip(alice_bits, alice_bases):
        
        qubit = QuantumCircuit(1, 1)
        
        if alice_bit == '1':
            qubit.x(0)
            
        if alice_base == 'X':
            qubit.h(0)
            
        qubit.barrier()
        
        qubits.append(qubit)
        
        
    # Bob side
    
    bob_bases = "XZZZ"
    
    bob_bits = []
    
    for qubit, bob_base in zip(qubits, bob_bases):
        
        if bob_base == 'X':
            
            qubit.h(0)
            
        qubit.measure(0, 0)
        
        simulator = Aer.get_backend('aer_simulator')
        
        qobj = assemble(qubit, shots=1, memory=True)
        
        result = simulator.run(qobj).result()
        
        bob_bit = int(result.get_memory()[0])
        
        bob_bits.append(bob_bit)
            
            
    # Filter bits
    
    alice_filtered_bits = []
    
    for alice_base, bob_base, alice_bit in zip(alice_bases, bob_bases, alice_bits):
        
        if alice_base == bob_base:
            
            alice_filtered_bits.append(alice_bit)
            
    
    bob_filtered_bits = []
    
    for alice_base, bob_base, bob_bit in zip(alice_bases, bob_bases, bob_bits):
        
        if alice_base == bob_base:
            
            bob_filtered_bits.append(bob_bit)
            
    

            

    
    # Logs
    
    task_log(f'BB84 run_values: {run_values}')
    
    task_log(f'BB84 alice_bits: {alice_bits}')
    task_log(f'BB84 alice_bases: {alice_bases}')
    
    task_log(f'BB84 bob_bases: {bob_bases}')
    task_log(f'BB84 bob_bits: {bob_bits}')
    
    task_log(f'BB84 alice_filtered_bits: {alice_filtered_bits}')
    task_log(f'BB84 bob_filtered_bits: {bob_filtered_bits}')