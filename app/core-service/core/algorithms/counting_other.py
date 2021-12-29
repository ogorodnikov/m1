

def build_unitary_phase_oracle(secrets, qubits_count):
    
    phase_oracle_circuit = QuantumCircuit(qubits_count + 1)
    
    ancilla_qubit = qubits_count
    
    phase_oracle_circuit.x(ancilla_qubit)
    phase_oracle_circuit.h(ancilla_qubit)
    
    for secret in secrets:
        
        control_qubits = [qubit_index for qubit_index, secret_digit in enumerate(secret) 
                          if secret_digit == '1']
        
        phase_oracle_circuit.mct(control_qubits, ancilla_qubit)
        
    phase_oracle_circuit.h(ancilla_qubit)
    phase_oracle_circuit.x(ancilla_qubit)
        
    phase_oracle_circuit.name = 'Unitary Phase Oracle'
    
    print(f'COUNT secrets: {secrets}')
    print(f'COUNT phase_oracle_circuit:\n{phase_oracle_circuit}')
    
    return phase_oracle_circuit
    

def build_grover_iteration(qubits_count, secrets):
    
    qubits = range(qubits_count)
    ancilla_qubit = qubits_count
    
    grover_iteration_circuit = QuantumCircuit(qubits_count + 1)
    
    phase_oracle = build_unitary_phase_oracle(secrets=secrets, qubits_count=qubits_count)
    diffuser = build_diffuser(qubits_count=qubits_count)
    
    grover_iteration_circuit.append(phase_oracle, [*qubits, ancilla_qubit])
    grover_iteration_circuit.append(diffuser, qubits)
    
    print(f'COUNT phase_oracle:\n{phase_oracle}')
    print(f'COUNT [*qubits, ancilla_qubit]: {[*qubits, ancilla_qubit]}')
    print(f'COUNT grover_iteration_circuit:\n{grover_iteration_circuit}')
    
    
    
    controlled_phase_oracle = phase_oracle.control()
    # controlled_diffuser = diffuser.control()

    
    return grover_iteration_circuit