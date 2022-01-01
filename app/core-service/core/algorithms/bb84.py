from qiskit import QuantumCircuit

from qiskit import Aer, assemble


def bb84(run_values, task_log):
    
    
    # Alice side
    
    alice_bits = '101010'
    
    alice_bases = 'XXXZXX'
    
    qubits = []
    
    for alice_bit, alice_base in zip(alice_bits, alice_bases):
        
        qubit = QuantumCircuit(1, 1)
        
        if alice_bit == '1':
            qubit.x(0)
            
        if alice_base == 'X':
            qubit.h(0)
            
        qubit.barrier()
        
        qubits.append(qubit)
        

    # Eve's side
    
    eve_bases = "XZZZXZ"
    
    eve_bits = []

    for qubit, eve_base in zip(qubits, eve_bases):
        
        if eve_base == 'X':
            
            qubit.h(0)
            
        qubit.measure(0, 0)
        
        if eve_base == 'X':
            
            qubit.h(0)
        
        simulator = Aer.get_backend('aer_simulator')
        
        qobj = assemble(qubit, shots=1, memory=True)
        
        result = simulator.run(qobj).result()
        
        eve_bit = result.get_memory()[0]
        
        eve_bits.append(eve_bit)    
        
        
    # Bob side
    
    bob_bases = "XXXZZZ"
    
    bob_bits = []
    
    for qubit, bob_base in zip(qubits, bob_bases):
        
        if bob_base == 'X':
            
            qubit.h(0)
            
        qubit.measure(0, 0)
        
        simulator = Aer.get_backend('aer_simulator')
        
        qobj = assemble(qubit, shots=1, memory=True)
        
        result = simulator.run(qobj).result()
        
        bob_bit = result.get_memory()[0]
        
        bob_bits.append(bob_bit)
        
        
        
            
    # Filter bits
    
    alice_key = []
    
    for alice_base, bob_base, alice_bit in zip(alice_bases, bob_bases, alice_bits):
        
        if alice_base == bob_base:
            
            alice_key.append(alice_bit)
            
    
    bob_key = []
    
    for alice_base, bob_base, bob_bit in zip(alice_bases, bob_bases, bob_bits):
        
        if alice_base == bob_base:
            
            bob_key.append(bob_bit)
            
    
    # Sample comparison
    
    sample_indices = [0, 2]
    
    sample_len = len(sample_indices)
    
    alice_sample = []
    bob_sample = []
    
    for sample_index in sample_indices:
        
        alice_sample.append(alice_key[sample_index])
        bob_sample.append(bob_key[sample_index])
    
    samples_fit = alice_sample == bob_sample
    
    key_length = len(alice_key)
    
    
    # Reliability calculation
    
    bases_count = max(map(len, map(set, (alice_bases, eve_bases, bob_bases))))
    
    basis_match_probability = 1 / bases_count
    
    states = [0, 1]
    
    states_count = len(set(states))
    
    state_match_probability = 1 / states_count
    
    single_qubit_evesdropping_detected_probability = basis_match_probability * state_match_probability
    single_qubit_evesdropping_undetected_probability = 1 - single_qubit_evesdropping_detected_probability
    
    total_evesdropping_undetected_probability = single_qubit_evesdropping_undetected_probability ** sample_len
    total_evesdropping_detected_probability = 1 - total_evesdropping_undetected_probability

    
    # Logs
    
    task_log(f'BB84 run_values: {run_values}')
    
    task_log(f'BB84 alice_bits: {alice_bits}')
    task_log(f'BB84 alice_bases: {alice_bases}')
    
    task_log(f'BB84 eve_bases: {eve_bases}')
    task_log(f'BB84 eve_bits: {eve_bits}')
    
    task_log(f'BB84 bob_bases: {bob_bases}')
    task_log(f'BB84 bob_bits: {bob_bits}')
    
    task_log(f'BB84 alice_key: {alice_key}')
    task_log(f'BB84 bob_key: {bob_key}')
    
    task_log(f'BB84 alice_sample: {alice_sample}')
    task_log(f'BB84 bob_sample: {bob_sample}')
    
    task_log(f'BB84 samples_fit: {samples_fit}')
    task_log(f'BB84 key_length: {key_length}')
    
    task_log(f'BB84 qubits:\n{[print(qubit) for qubit in qubits]}')
 
    task_log(f'BB84 single_qubit_evesdropping_undetected_probability: {single_qubit_evesdropping_undetected_probability}')  
    task_log(f'BB84 single_qubit_evesdropping_detected_probability: {single_qubit_evesdropping_detected_probability}')  
    
    task_log(f'BB84 total_evesdropping_undetected_probability: {total_evesdropping_undetected_probability}')  
    task_log(f'BB84 total_evesdropping_detected_probability: {total_evesdropping_detected_probability}')  
    