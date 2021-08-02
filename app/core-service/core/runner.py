import time
import traceback

from multiprocessing import Process, Event, Queue, Manager

from queue import PriorityQueue

from qiskit import IBMQ, Aer, execute
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import backend_overview, job_monitor

from core import app


def log(task_id, message):

    app.logger.info(f'{message}')
    
    if task_id in logs:
        logs[task_id] += [message]
    else:
        logs[task_id] = [message]


from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz
from core.algorithms.grover import grover
from core.algorithms.grover_sudoku import grover_sudoku


runner_functions = {'egcd': egcd,
                    'bernvaz': bernvaz,
                    'grover': grover,
                    'grover_sudoku': grover_sudoku,
                   }

task_process_count = app.config.get('CPU_COUNT', 1)

task_id = 0          
task_queue = Queue()
task_results_queue = Queue()
tasks = {}

manager = Manager()
logs = manager.dict()

worker_active_flag = Event()
worker_active_flag.set()

task_worker_processes = []


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
    app.logger.info(f'RUNNER task_queue: {task_queue}')
    app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
    app.logger.info(f'RUNNER task_id: {task_id}')
    
    return task_id
    

def start_task_worker_processes():
    
    for i in range(task_process_count):
    
        task_worker_process = Process(target=task_worker,
                                      args=(task_queue, task_results_queue, worker_active_flag),
                                      daemon=True)
                                              
        task_worker_process.start()
        
        task_worker_processes.append(task_worker_process)
        

def task_worker(task_queue, task_results_queue, worker_active_flag):
    
    app.logger.info(f'RUNNER task_worker started')
    
    while True:
        
        time.sleep(1)
        
        if worker_active_flag.is_set() and not task_queue.empty():
            
            pop_task = task_queue.get()
            
            priority, task_id, algorithm_id, run_values = pop_task
            
            app.logger.info(f'RUNNER pop_task: {pop_task}')
            app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')

            try:
                
                result = task_runner(task_id, algorithm_id, run_values)
                
            except Exception as exception:
                
                status = 'Failed'
                
                error_message = traceback.format_exc()
                log(task_id, error_message)
                
            else:
                
                status = 'Done'
            
            task_results_queue.put((task_id, result, status))

            log(task_id, f'result: {result}')
            log(task_id, f'status: {status}')
            
            app.logger.info(f'task_results_queue.qsize: {task_results_queue.qsize()}')
            app.logger.info(f'len(tasks): {len(tasks)}')
        

def task_runner(task_id, algorithm_id, run_values_multidict):
    
    run_values = dict(run_values_multidict)
    run_values['task_id'] = task_id
    
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
        
        log(task_id, f'RUNNER provider: {provider}')
        log(task_id, f'RUNNER provider.backends(): {provider.backends()}')

        backend = get_least_busy_backend(provider, qubit_count)
        
    log(task_id, f'RUNNER backend: {backend}')

    job = execute(circuit, backend=backend, shots=1024)
    
    job_monitor(job, interval=0.5)
    
    result = job.result()
    
    counts = result.get_counts()
    
    log(task_id, f'RUNNER counts:')
    [log(task_id, f'{state}: {count}') for state, count in sorted(counts.items())]
    
    return {'Counts:': counts}
    

def get_task_results():
    
    while not task_results_queue.empty():
        
        task_result = task_results_queue.get()
        
        task_id, result, status = task_result
        
        tasks[task_id]['result'] = result            
        tasks[task_id]['status'] = status
        
        yield task_result

    
def get_least_busy_backend(provider, qubit_count):

    backend_filter = lambda backend: (not backend.configuration().simulator 
                                      and backend.configuration().n_qubits >= qubit_count
                                      and backend.status().operational==True)
        
    least_busy_backend = least_busy(provider.backends(filters=backend_filter))
    
    return least_busy_backend