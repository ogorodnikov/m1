def dj():
    pass


# from itertools import combinations

# from qiskit import Aer, ClassicalRegister, QuantumRegister, QuantumCircuit, execute
# from qiskit.tools.monitor import job_monitor

# from core.runner import log


# ONE_STATE = 0, 1
# ZERO_STATE = 1, 0
# MINUS_STATE = 2**-0.5, -(2**-0.5)

# DEFAULT_SOLUTIONS_COUNT = 2
# DEFAULT_REPETITIONS_LIMIT = 3

# # run_values = {'input_row_1': '1.',
# #               'input_row_2': '.',
# #               'input_row_3': '',
# #               'sudoku_width': 'autodetect',
# #               'sudoku_height': 'autodetect',
# #               'maximum_digit': 'autodetect',
# #               'repetitions_limit': '3',
# #               'solutions_count': '2',
# #               'run_mode': 'simulator',                 
# #             #   'run_mode': 'quantum_device',                 
# #              }


# def initialize_sudoku_circuit(circuit, sudoku_rows, qubits_per_cell, output_qubit):
    
#     sudoku_height = len(sudoku_rows)
#     sudoku_width = len(sudoku_rows[0])
    
#     for y in range(sudoku_height):
#         for x in range(sudoku_width):
            
#             cell_base_index = (x + y * sudoku_width) * qubits_per_cell
            
#             cell_value = sudoku_rows[y][x]
            
#             try:
                
#                 cell_integer = int(cell_value)
#                 cell_binary = f'{cell_integer:0{qubits_per_cell}b}'
                
#                 for bit_index, bit in enumerate(reversed(cell_binary)):
                
#                     cell_qubit = cell_base_index + bit_index
                    
#                     if bit == '1':
#                         state = ONE_STATE
#                     else:
#                         state = ZERO_STATE

#                     print('state:', state)

#                     circuit.initialize(state, cell_qubit)

#             except ValueError:
                
#                 for bit_index in range(qubits_per_cell):
                
#                     cell_qubit = cell_base_index + bit_index
                    
#                     circuit.h(cell_qubit)
                
#     circuit.initialize(MINUS_STATE, output_qubit)
    
#     return circuit


# def build_sudoku_oracle(cell_qubits_count, pair_qubits_count, 
#                         pairs, qubits_per_cell, sudoku_width):
    
#     sudoku_oracle_circuit = QuantumCircuit(cell_qubits_count + pair_qubits_count)

#     for pair_index, pair in enumerate(pairs):
        
#         (ax, ay), (bx, by) = pair
        
#         a_base_index = (ax + ay * sudoku_width) * qubits_per_cell
#         b_base_index = (bx + by * sudoku_width) * qubits_per_cell
        
#         pair_base_index = cell_qubits_count + pair_index * qubits_per_cell
        
#         for position_index in range(qubits_per_cell):
        
#             a_qubit = a_base_index + position_index
#             b_qubit = b_base_index + position_index
            
#             pair_qubit = pair_base_index + position_index
    
#             sudoku_oracle_circuit.cx(a_qubit, pair_qubit)
#             sudoku_oracle_circuit.cx(b_qubit, pair_qubit)
            
#             sudoku_oracle_circuit.barrier()
        
#     sudoku_oracle_circuit.name = "Sudoku Oracle"
    
#     return sudoku_oracle_circuit
    

# def build_diffuser(qubit_count):
    
#     diffuser_circuit = QuantumCircuit(qubit_count)
        
#     for qubit in range(qubit_count):
#         diffuser_circuit.h(qubit)

#     for qubit in range(qubit_count):
#         diffuser_circuit.x(qubit)
        
#     for qubit in range(1, qubit_count):
#         diffuser_circuit.i(qubit)

#     diffuser_circuit.h(0)
#     diffuser_circuit.mct(list(range(1, qubit_count)), 0)
#     diffuser_circuit.h(0)
    
#     for qubit in range(1, qubit_count):
#         diffuser_circuit.i(qubit)

#     for qubit in range(qubit_count):
#         diffuser_circuit.x(qubit)

#     for qubit in range(qubit_count):
#         diffuser_circuit.h(qubit)
        
#     diffuser_circuit.name = 'Diffuser'
    
#     return diffuser_circuit
    

# def parse_run_values(run_values):
    
#     task_id = run_values.get('task_id')
#     run_mode = run_values.get('run_mode')
    
#     input_width = run_values.get('width')
#     input_height = run_values.get('height')
#     input_maximum_digit = run_values.get('maximum_digit')
    
#     input_solutions_count = run_values.get('solutions_count')
#     input_repetitions_limit = run_values.get('repetitions_limit')

#     input_rows = [value for key, value in run_values.items() if 'row' in key and value]
    
    
#     if input_width.isdecimal():
#         sudoku_width = int(input_width)
#     else:
#         sudoku_width = max(map(len, input_rows))
        
#     # print('sudoku_width:', sudoku_width)
        
#     sized_rows = [row.ljust(sudoku_width, '.')[:sudoku_width] for row in input_rows]
    
#     # print('sized_rows:', sized_rows)    
        
#     input_columns = [''.join(element) for element in zip(*sized_rows)]
    
#     # print('input_columns:', input_columns) 
    
    
#     if input_height.isdecimal():
#         sudoku_height = int(input_height)
#     else:
#         sudoku_height = max(map(len, input_columns))
        
#     # print('sudoku_height:', sudoku_height)    
        
#     sized_columns = [column.ljust(sudoku_height, '.')[:sudoku_height] for column in input_columns]

#     # print('sized_columns:', sized_columns)
    
#     sudoku_rows = [''.join(element) for element in zip(*sized_columns)]
    
#     # print('sudoku_rows:', sudoku_rows)
    
#     sudoku_integers = [int(symbol) for row in sudoku_rows 
#                       for symbol in row 
#                       if symbol.isdecimal()]
                       

#     if input_maximum_digit.isdecimal():
#         sudoku_maximum_digit = int(input_maximum_digit)
#     else:
#         sudoku_maximum_digit = max(sudoku_integers)
    
#     # print('sudoku_maximum_digit:', sudoku_maximum_digit)
    
    
#     if input_solutions_count.isdecimal():
#         solutions_count = int(input_solutions_count)
#     else:
#         solutions_count = DEFAULT_SOLUTIONS_COUNT
        
#     if input_repetitions_limit.isdecimal():
#         repetitions_limit = int(input_repetitions_limit)
#     else:
#         repetitions_limit = DEFAULT_REPETITIONS_LIMIT


#     return sudoku_rows, sudoku_height, sudoku_width, \
#     sudoku_integers, sudoku_maximum_digit, run_mode, \
#     solutions_count, repetitions_limit, task_id


# def grover_sudoku(run_values):
    
#     sudoku_rows, sudoku_height, sudoku_width, \
#     sudoku_integers, sudoku_maximum_digit, run_mode, \
#     solutions_count, repetitions_limit, task_id = parse_run_values(run_values)

#     cells_count = sudoku_height * sudoku_width
    
    
#     row_pairs = sorted(((a, row_index), (b, row_index)) 
#                       for a, b in combinations(range(sudoku_width), 2)
#                       for row_index in range(sudoku_height))
                 
#     column_pairs = sorted(((column_index, a), (column_index, b)) 
#                           for a, b in combinations(range(sudoku_height), 2)
#                           for column_index in range(sudoku_width))
    
#     pairs = row_pairs + column_pairs
#     pairs_count = len(pairs)
                       
#     possible_integers = sudoku_integers + [sudoku_maximum_digit]
                       
#     qubits_per_cell = max(map(int.bit_length, possible_integers))
    
#     cell_qubits_count = cells_count * qubits_per_cell
#     pair_qubits_count = pairs_count * qubits_per_cell
    
#     cell_qubits = QuantumRegister(cell_qubits_count, name='c')
#     pair_qubits = QuantumRegister(pair_qubits_count, name='p')
    
#     output_qubit = QuantumRegister(1, name='out')
#     output_bits = ClassicalRegister(cell_qubits_count, name='b')
    
#     initial_circuit = QuantumCircuit(cell_qubits, pair_qubits, 
#                                      output_qubit, output_bits)
    
#     circuit = initialize_sudoku_circuit(initial_circuit, sudoku_rows, 
#                                         qubits_per_cell, output_qubit)
    
#     sudoku_oracle = build_sudoku_oracle(cell_qubits_count, pair_qubits_count, 
#                                         pairs, qubits_per_cell, sudoku_width)

#     defined_qubits_count = len(sudoku_integers) * qubits_per_cell

#     elements_count = 2 ** (cell_qubits_count - defined_qubits_count)
    
#     repetitions = (elements_count / solutions_count) ** 0.5 * 3.14 / 4
    
#     limited_repetitions = min(int(repetitions), repetitions_limit)
    
#     repetitions_count = max(limited_repetitions, 1)
    

#     for i in range(repetitions_count):
    
#         circuit.append(sudoku_oracle, range(cell_qubits_count + pair_qubits_count))
        
#         circuit.mct(pair_qubits, output_qubit)
        
#         circuit.append(sudoku_oracle, range(cell_qubits_count + pair_qubits_count))
        
#         diffuser = build_diffuser(cell_qubits_count)
        
#         circuit.append(diffuser, cell_qubits)


#     circuit.measure(cell_qubits, output_bits)
    
#     log(task_id, f'SUDOKU task_id: {task_id}')
#     log(task_id, f'SUDOKU run_values: {run_values}')
#     log(task_id, f'SUDOKU sudoku_maximum_digit: {sudoku_maximum_digit}')
#     log(task_id, f'SUDOKU sudoku_rows: {sudoku_rows}')
#     log(task_id, f'SUDOKU sudoku_integers: {sudoku_integers}')
#     log(task_id, f'SUDOKU qubits_per_digit: {qubits_per_cell}')
    
#     log(task_id, f'SUDOKU cells_count: {cells_count}') 
#     log(task_id, f'SUDOKU cell_qubits_count: {cell_qubits_count}') 
#     log(task_id, f'SUDOKU pairs: {pairs}')
#     log(task_id, f'SUDOKU pairs_count: {pairs_count}')
#     log(task_id, f'SUDOKU pair_qubits_count: {pair_qubits_count}')
    
#     log(task_id, f'SUDOKU elements_count: {elements_count}')
#     log(task_id, f'SUDOKU repetitions: {repetitions}')
#     log(task_id, f'SUDOKU repetitions_count: {repetitions_count}')
    
#     log(task_id, f'SUDOKU sudoku_oracle: \n{sudoku_oracle}')
#     log(task_id, f'SUDOKU circuit: \n{circuit}')

#     return circuit