from queue import PriorityQueue

import threading
import time

from core import app

from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz
from core.algorithms.grover import grover

from concurrent.futures import ThreadPoolExecutor

from qiskit import IBMQ, Aer, execute
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import backend_overview, job_monitor


TASK_WORKERS_COUNT = 2

runner_functions = {'egcd': egcd,
                    'bernvaz': bernvaz,
                    'grover': grover,    
                   }



task_id = 0          
task_queue = PriorityQueue()
result_queue = PriorityQueue()
tasks = {}

worker_active_flag = threading.Event()
worker_active_flag.set()

task_workers = []

def task_worker(task_queue, result_queue, worker_active_flag):
    
    app.logger.info(f'RUNNER task_worker started')
    
    while True:
        
        time.sleep(1)
    
        if worker_active_flag.is_set() and not task_queue.empty():
            
            pop_task = task_queue.get()
            
            priority, task_id, algorithm_id, run_values = pop_task
            
            app.logger.info(f'RUNNER pop_task: {pop_task}')
            app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')

            result = task_runner(algorithm_id, run_values)
            
            result_queue.put((task_id, result))

            tasks[task_id]['result'] = result            
            tasks[task_id]['status'] = 'Done'
            
            app.logger.info(f'RUNNER result: {result}')
            app.logger.info(f'RUNNER result_queue.qsize: {result_queue.qsize()}')
            app.logger.info(f'RUNNER len(tasks): {len(tasks)}')

for i in range(TASK_WORKERS_COUNT):

    task_worker_thread = threading.Thread(target=task_worker,
                                          args=(task_queue, result_queue, worker_active_flag),
                                          daemon=True)
                                          
    task_worker_thread.start()
    
    task_workers.append(task_worker_thread)
    
app.logger.info(f'RUNNER task_workers: {task_workers}')
    

def run_algorithm(algorithm_id, run_values):
    
    priority = 1

    global task_id
    task_id += 1
    
    new_task = (priority, task_id, algorithm_id, run_values)
    
    tasks[task_id] = {'algorithm_id': algorithm_id,
                      'run_values': run_values,
                      'status': 'Running'}
                      
    task_queue.put(new_task)
    
    app.logger.info(f'RUNNER new_task: {new_task}')
    app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
    app.logger.info(f'RUNNER task_id: {task_id}')
    
    return task_id
    

def task_runner(algorithm_id, run_values):
    
    runner_function = runner_functions[algorithm_id]
    
    run_mode = run_values.get('run_mode')
    
    app.logger.info(f'RUNNER run_mode: {run_mode}')
    app.logger.info(f'RUNNER run_values: {run_values}')
    app.logger.info(f'RUNNER runner_function: {runner_function}')  
    
    if run_mode == 'classic':
        
        return runner_function(run_values)
    
    else:
    
        circuit = runner_function(run_values)
        
        qubit_count = circuit.num_qubits
        
    if run_mode == 'simulator':
        
        backend = Aer.get_backend('qasm_simulator')
        
    elif run_mode == 'quantum_device':
    
        qiskit_token = app.config.get('QISKIT_TOKEN')
        IBMQ.save_account(qiskit_token)
        
        if not IBMQ.active_account():
            IBMQ.load_account()
            
        provider = IBMQ.get_provider()
        
        app.logger.info(f'RUNNER provider: {provider}')
        app.logger.info(f'RUNNER provider.backends(): {provider.backends()}')
        
        # backend = provider.get_backend('ibmq_manila')

        backend = get_least_busy_backend(provider, qubit_count)
        
    app.logger.info(f'RUNNER backend: {backend}')

    job = execute(circuit, backend=backend, shots=1024)
    
    job_monitor(job, interval=5)
    
    result = job.result()
    
    counts = result.get_counts()
    
    app.logger.info(f'GROVER counts:')
    [app.logger.info(f'{state}: {count}') for state, count in sorted(counts.items())]

    return {'Counts:': counts}


def get_least_busy_backend(provider, qubit_count):
    
    # backend_overview()
    
    backend_filter = lambda backend: (not backend.configuration().simulator 
                                      and backend.configuration().n_qubits >= qubit_count
                                      and backend.status().operational==True)
        
    least_busy_backend = least_busy(provider.backends(filters=backend_filter))
    
    return least_busy_backend