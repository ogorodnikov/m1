from qiskit import QuantumCircuit


def bb84(run_values, task_log):
    
    # Inputs
    
    alice_bits = run_values['alice_bits']
    
    alice_bases = run_values['alice_bases']
    
    eve_bases = run_values['eve_bases']
    bob_bases = run_values['bob_bases']
    bob_bases = run_values['bob_bases']

    sample_indices_input = run_values['sample_indices']
    
    message_len = len(alice_bits)
    
    
    # Alice side
    
    circuit = QuantumCircuit(message_len, message_len * 2)
    
    for qubit_index, (alice_bit, alice_base) in enumerate(zip(alice_bits, alice_bases)):
        
        if alice_bit == '1':
            circuit.x(qubit_index)
            
        if alice_base == 'X':
            circuit.h(qubit_index)
            
    circuit.barrier()
    
        
    # Eve side
    
    for qubit_index, eve_base in enumerate(eve_bases):
        
        if eve_base == 'X':
            circuit.h(qubit_index)
            
        circuit.measure(qubit_index, qubit_index)
        
        if eve_base == 'X':
            circuit.h(qubit_index)
            
        circuit.barrier()
            

    # Bob side
    
    for qubit_index, bob_base in enumerate(bob_bases):
        
        if bob_base == 'X':
            circuit.h(qubit_index)
            
        circuit.measure(qubit_index, message_len + qubit_index)
            
        circuit.barrier()
        
            
    # Logs
    
    task_log(f'\nBB84 Circuit Composition:\n')
    
    task_log(f'BB84 run_values: {run_values}')
    
    task_log(f'BB84 alice_bits: {alice_bits}')
    
    task_log(f'BB84 alice_bases: {alice_bases}')
    task_log(f'BB84 eve_bases: {eve_bases}')
    task_log(f'BB84 bob_bases: {bob_bases}')
    
    task_log(f'BB84 sample_indices_input: {sample_indices_input}')
    task_log(f'BB84 message_len: {message_len}')
    
    task_log(f'\nBB84 circuit:\n{circuit}')
    
    return circuit


def bb84_post_processing(run_data, task_log):
    
    # Inputs
    
    run_values = run_data['Run Values']
    counts = run_data['Result']['Counts']
    
    alice_bits = run_values['alice_bits']
    
    alice_bases = run_values['alice_bases']
    eve_bases = run_values['eve_bases']
    bob_bases = run_values['bob_bases']

    sample_indices_input = run_values['sample_indices']
    
    
    # Parameters
    
    sample_indices_split = sample_indices_input.split(',')
    sample_indices = list(map(int, map(str.strip, sample_indices_split)))
    
    sample_len = len(sample_indices)
    message_len = len(alice_bits)
    
    max_state = max(counts, key=counts.get)
    
    bob_bits = ''.join(reversed(max_state[:message_len]))
    eve_bits = ''.join(reversed(max_state[-message_len:]))


    # Keys
    
    alice_key = ''
    
    for alice_base, bob_base, alice_bit in zip(alice_bases, bob_bases, alice_bits):
        
        if alice_base == bob_base:
            
            alice_key += alice_bit
            
    
    bob_key = ''
    
    for alice_base, bob_base, bob_bit in zip(alice_bases, bob_bases, bob_bits):
        
        if alice_base == bob_base:
            
            bob_key += bob_bit
    
    key_length = len(alice_key)
    
    
    # Sample comparison
    
    alice_sample = ''
    bob_sample = ''
    
    for sample_index in sample_indices:
        
        alice_sample += alice_key[sample_index]
        bob_sample += bob_key[sample_index]

    samples_match = alice_sample == bob_sample
    
    evesdropping_detected = not samples_match
    
    result = {'Evesdropping Detected': evesdropping_detected}
    
    
    # Reliability Calculation
    
    bases_count = max(map(len, map(set, (alice_bases, eve_bases, bob_bases))))
    
    basis_match_probability = 1 / bases_count
    
    possible_states = [0, 1]
    
    states_count = len(set(possible_states))
    
    state_match_probability = 1 / states_count
    
    single_qubit_evesdropping_detected_probability = basis_match_probability * state_match_probability
    single_qubit_evesdropping_undetected_probability = 1 - single_qubit_evesdropping_detected_probability
    
    total_evesdropping_undetected_probability = single_qubit_evesdropping_undetected_probability ** sample_len
    total_evesdropping_detected_probability = 1 - total_evesdropping_undetected_probability

    
    # Logs
    
    task_log(f'\nBB84 Post Processing:\n')
    
    task_log(f'BB84 counts: {counts}')
    task_log(f'BB84 max_state: {max_state}')
    
    task_log(f'BB84 run_values: {run_values}')
    
    task_log(f'BB84 alice_bits: {alice_bits}')
    task_log(f'BB84 alice_bases: {alice_bases}')
    
    task_log(f'BB84 eve_bases: {eve_bases}')
    task_log(f'BB84 eve_bits: {eve_bits}')
    
    task_log(f'BB84 bob_bases: {bob_bases}')
    task_log(f'BB84 bob_bits: {bob_bits}')
    
    task_log(f'BB84 alice_key: {alice_key}')
    task_log(f'BB84 bob_key: {bob_key}')
    task_log(f'BB84 key_length: {key_length}')
    
    task_log(f'BB84 alice_sample: {alice_sample}')
    task_log(f'BB84 bob_sample: {bob_sample}')
    
    task_log(f'BB84 samples_match: {samples_match}')
    task_log(f'BB84 evesdropping_detected: {evesdropping_detected}')

    task_log(f'BB84 result: {result}')

    task_log(f'\nBB84 Reliability Calculation:\n')
    
    task_log(f'BB84 single_qubit_evesdropping_undetected_probability: {single_qubit_evesdropping_undetected_probability}')  
    task_log(f'BB84 single_qubit_evesdropping_detected_probability: {single_qubit_evesdropping_detected_probability}')  
    
    task_log(f'BB84 total_evesdropping_undetected_probability: {total_evesdropping_undetected_probability}')  
    task_log(f'BB84 total_evesdropping_detected_probability: {total_evesdropping_detected_probability}')
    task_log(f'')
    
    return result