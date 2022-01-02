from qiskit import QuantumCircuit

from qiskit import Aer, assemble


def bb84(run_values, task_log):
    
    # Inputs
    
    alice_bits = run_values['alice_bits']
    
    alice_bases = run_values['alice_bases']
    eve_bases = run_values['eve_bases']
    bob_bases = run_values['bob_bases']
    
    bob_bases = run_values['bob_bases']

    sample_indices_input = run_values['sample_indices'].split(',')
    sample_indices = list(map(int, map(str.strip, sample_indices_input)))
    
    sample_len = len(sample_indices)
    
    message_len = len(alice_bits)
    
    
    # Alice side
    
    circuit = QuantumCircuit(message_len, message_len * 2)
    
    for qubit_index, (alice_bit, alice_base) in enumerate(zip(alice_bits, alice_bases)):
        
        if alice_bit == '1':
            circuit.x(qubit_index)
            
        if alice_base == 'X':
            circuit.h(qubit_index)
            
    circuit.barrier()
    
        
    # Eve's side
    
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
            
    # simulator = Aer.get_backend('aer_simulator')
    
    # qobj = assemble(circuit, shots=1, memory=True)
    
    # result = simulator.run(qobj).result()
    
    # all_bits = result.get_memory()[0]
    
    all_bits = '010011010011'
    
    bob_bits = list(reversed(all_bits[:message_len]))

    eve_bits = list(reversed(all_bits[-message_len:]))

    # print(result.get_memory())
    # print(result.get_counts())
    # print(eve_bits)
    
    # quit()
    

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
    
    task_log(f'BB84 circuit:\n{circuit}')
    
    task_log(f'BB84 all_bits: {all_bits}')
 
    task_log(f'BB84 single_qubit_evesdropping_undetected_probability: {single_qubit_evesdropping_undetected_probability}')  
    task_log(f'BB84 single_qubit_evesdropping_detected_probability: {single_qubit_evesdropping_detected_probability}')  
    
    task_log(f'BB84 total_evesdropping_undetected_probability: {total_evesdropping_undetected_probability}')  
    task_log(f'BB84 total_evesdropping_detected_probability: {total_evesdropping_detected_probability}')
    
    return circuit


def bb84_post_processing(run_data, task_log):
    
    run_values = run_data['Run Values']
    counts = run_data['Result']['Counts']
    
    max_state = max(counts, key=counts.get)
    
    # Inputs
    
    alice_bits = run_values['alice_bits']
    
    alice_bases = run_values['alice_bases']
    eve_bases = run_values['eve_bases']
    bob_bases = run_values['bob_bases']
    
    bob_bases = run_values['bob_bases']

    sample_indices_input = run_values['sample_indices'].split(',')
    sample_indices = list(map(int, map(str.strip, sample_indices_input)))
    
    sample_len = len(sample_indices)
    
    message_len = len(alice_bits)
    
    
    all_bits = max_state
    
    bob_bits = list(reversed(all_bits[:message_len]))

    eve_bits = list(reversed(all_bits[-message_len:]))

    # print(result.get_memory())
    # print(result.get_counts())
    # print(eve_bits)
    
    # quit()
    

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
    
    task_log(f'BB84 alice_sample: {alice_sample}')
    task_log(f'BB84 bob_sample: {bob_sample}')
    
    task_log(f'BB84 samples_fit: {samples_fit}')
    task_log(f'BB84 key_length: {key_length}')
    
    
    task_log(f'BB84 all_bits: {all_bits}')
 
    task_log(f'BB84 single_qubit_evesdropping_undetected_probability: {single_qubit_evesdropping_undetected_probability}')  
    task_log(f'BB84 single_qubit_evesdropping_detected_probability: {single_qubit_evesdropping_detected_probability}')  
    
    task_log(f'BB84 total_evesdropping_undetected_probability: {total_evesdropping_undetected_probability}')  
    task_log(f'BB84 total_evesdropping_detected_probability: {total_evesdropping_detected_probability}')