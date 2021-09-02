import time
import traceback

from os import getpid, _exit
from functools import partial
from multiprocessing import Process, Event, Queue, Manager

from qiskit import IBMQ, Aer, execute
from qiskit.providers.ibmq import least_busy
from qiskit.visualization import plot_bloch_multivector
from qiskit.tools.monitor import backend_overview, job_monitor

from core import app


def task_log(task_id, message):

    app.logger.info(f'{message}')
    
    logs[task_id] += [message]


from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz
from core.algorithms.grover import grover
from core.algorithms.grover_sudoku import grover_sudoku
from core.algorithms.dj import dj
from core.algorithms.simon import simon, simon_post_processing
from core.algorithms.qft import qft
from core.algorithms.qpe import qpe


runner_functions = {'egcd': egcd,
                    'bernvaz': bernvaz,
                    'grover': grover,
                    'grover_sudoku': grover_sudoku,
                    'dj': dj,
                    'simon': simon,
                    'qft': qft,
                    'qpe': qpe
                   }
                   
post_processing = {'simon': simon_post_processing}

task_process_count = app.config.get('CPU_COUNT', 1)


### Test

# task_process_count = 2


task_rollover_size = app.config.get('TASK_ROLLOVER_SIZE', 100)

PLOT_STATEVECTOR_TIMEOUT = 5
TASK_TIMEOUT = 3

task_id = 0

task_queue = Queue()
task_results_queue = Queue()

manager = Manager()

app.logger.info(f'RUNNER manager: {manager}')

print()


logs = manager.dict()
tasks = manager.dict()

worker_active_flag = Event()
worker_active_flag.set()

task_worker_processes = []


def run_algorithm(algorithm_id, run_values):
    
    global task_id
    task_id = task_id % task_rollover_size + 1
    
    new_task = (task_id, algorithm_id, run_values)
    
    task_queue.put(new_task)
    
    new_task_record = {'algorithm_id': algorithm_id,
                       'run_values': run_values,
                       'status': 'Queued'}
                       
    tasks[task_id] = manager.dict(new_task_record)
    
    logs[task_id] = manager.list()
    
    app.logger.info(f'RUNNER task_id: {task_id}')
    app.logger.info(f'RUNNER new_task: {new_task}')
    app.logger.info(f'RUNNER task_queue: {task_queue}')
    app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
    
    return task_id
    

def start_task_worker_processes():
    
    for i in range(task_process_count):
    
        task_worker_process = HiddenDaemonProcess(
                                  target=task_worker,
                                  args=(task_queue, task_results_queue, worker_active_flag),
                                  daemon=True)
                                  
        app.logger.info(f'RUNNER task_worker_process: {task_worker_process}')                
        app.logger.info(f'RUNNER task_worker_process.daemon: {task_worker_process.daemon}')                
        app.logger.info(f'RUNNER task_worker_process.pid: {task_worker_process.pid}')                
                                              
        task_worker_process.start()
        
        task_worker_processes.append(task_worker_process)
        

def task_worker(task_queue, task_results_queue, worker_active_flag):
    
    process_id = getpid()
    
    app.logger.info(f'RUNNER task_worker started: {process_id}')
    
    while True:
        
        time.sleep(1)
        
        if worker_active_flag.is_set() and not task_queue.empty():
            
            pop_task = task_queue.get()
            
            task_id, algorithm_id, run_values = pop_task
            
            task_results_queue.put((task_id, '', 'Running'))
            
            app.logger.info(f'RUNNER pop_task: {pop_task}')
            app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
            
            try:
                
                result = None
                
                task_runner_process = Process(target=task_runner,
                                              args=(task_id, algorithm_id, run_values, result),
                                              name=f'Process-task-id-{task_id}',
                                              daemon=False)
                    
                
                # task_thread = threading.Thread(target=task_runner,
                #                               args=(task_id, algorithm_id, run_values, result),
                #                               name=f'Thread-{task_id}',
                #                               daemon=True)
                
                task_runner_process.start()
                task_runner_process.join(3)

                if task_runner_process.is_alive():
                    
                    app.logger.info(f'RUNNER task_runner_process.is_alive()')
                    
                    task_runner_process.terminate()
                    
                    raise TimeoutError
                    
                # result = task_runner(task_id, algorithm_id, run_values)
                
                status = 'Done'
                
                
                
            except Exception as exception:
                
                error_message = traceback.format_exc()
                task_log(task_id, error_message)
                
                result = None
                status = 'Failed'
            
            task_results_queue.put((task_id, result, status))

            task_log(task_id, f'RUNNER Result: {result}')
            task_log(task_id, f'RUNNER Status: {status}')
            
            app.logger.info(f'RUNNER task_results_queue.qsize: {task_results_queue.qsize()}')
            app.logger.info(f'RUNNER len(tasks): {len(tasks)}')
        

def task_runner(task_id, algorithm_id, run_values_multidict, result):
    
    run_values = dict(run_values_multidict)
    run_values['task_id'] = task_id
    
    runner_function = runner_functions[algorithm_id]
    
    run_mode = run_values.get('run_mode')
    
    app.logger.info(f'RUNNER run_mode: {run_mode}')
    app.logger.info(f'RUNNER run_values: {run_values}')
    app.logger.info(f'RUNNER runner_function: {runner_function}') 
    
    task_log_callback = partial(task_log, task_id)
    
    
    if run_mode == 'classical':
        
        result = runner_function(run_values, task_log_callback)
        
        time.sleep(1000)
        
        return
    
        # return runner_function(run_values, task_log_callback)
        
    
    elif run_mode == 'simulator':
        
        circuit = runner_function(run_values, task_log_callback)
        qubit_count = circuit.num_qubits
        
        backend = Aer.get_backend('qasm_simulator')
        
        circuit.save_statevector()
        
        result = execute_task(task_id, circuit, backend)
        
        # task_log(task_id, f'RUNNER result: {result}')

        counts = result.get_counts()
        
        # task_log(task_id, f'RUNNER counts: {counts}')
        
        statevector = result.get_statevector(decimals=3)
        
        plot_statevector_figure(task_id, statevector)

        task_log(task_id, f'RUNNER statevector:')
        
        for state_index, probability_amplitude in enumerate(statevector):
            
            if not probability_amplitude:
                continue
            
            state = f'{state_index:0{qubit_count}b}'
            
            task_log(task_id, f'{state}: {probability_amplitude}')
        
        
    elif run_mode == 'quantum_device':
    
        qiskit_token = app.config.get('QISKIT_TOKEN')
        IBMQ.save_account(qiskit_token)
        
        if not IBMQ.active_account():
            IBMQ.load_account()
            
        ibmq_provider = IBMQ.get_provider()
        
        task_log(task_id, f'RUNNER ibmq_provider: {ibmq_provider}')
        task_log(task_id, f'RUNNER ibmq_provider.backends(): {ibmq_provider.backends()}')
        
        circuit = runner_function(run_values, task_log_callback)
        qubit_count = circuit.num_qubits        

        backend = get_least_busy_backend(ibmq_provider, qubit_count)
        
        result = execute_task(task_id, circuit, backend)
        counts = result.get_counts()
        
        
    if algorithm_id not in post_processing:
        task_result = {'Counts': counts}
        
    else:
        task_result = post_processing[algorithm_id](counts, task_log_callback)
    
    task_log(task_id, f'RUNNER task_result: {task_result}')

    result = task_result
    
    # time.sleep(10)
    
    # return task_result
    
    
def execute_task(task_id, circuit, backend):
    
    task_log(task_id, f'RUNNER backend: {backend}')
    
    job = execute(circuit, backend=backend, shots=1024)
    
    job_monitor(job, interval=0.5)
    
    result = job.result()
    counts = result.get_counts()
    
    task_log(task_id, f'RUNNER counts:')
    [task_log(task_id, f'{state}: {count}') for state, count in sorted(counts.items())]
    
    return result
    

def get_task_results():
    
    while not task_results_queue.empty():
        
        task_result = task_results_queue.get()
        
        task_id, result, status = task_result
        
        tasks[task_id]['result'] = result            
        tasks[task_id]['status'] = status
        
        if status == 'Running':
            continue
        
        yield task_result

    
def get_least_busy_backend(provider, qubit_count):

    backend_filter = lambda backend: (not backend.configuration().simulator 
                                      and backend.configuration().n_qubits >= qubit_count
                                      and backend.status().operational==True)
        
    least_busy_backend = least_busy(provider.backends(filters=backend_filter))
    
    return least_busy_backend
    

def plot_statevector_figure(task_id, statevector):
        
    figure = plot_bloch_multivector(statevector)
    
    task_log(task_id, f'RUNNER figure: {figure}')        

    figure_path = app.static_folder + f'/figures/bloch_multivector_task_{task_id}.png'
                
    figure.savefig(figure_path, transparent=True, bbox_inches='tight')
    
    
def terminate_application(message):
    
    app.logger.info(f'RUNNER terminate_application: {message}')
    
    _exit(0)
    
    
class HiddenDaemonProcess(Process):

    @property
    def daemon(self):
        return False
        
    @daemon.setter
    def daemon(self, value):
        app.logger.info(f'RUNNER Before')
        app.logger.info(f'RUNNER super().daemon: {super().daemon}')
        app.logger.info(f'RUNNER self.daemon: {self.daemon}')

        super(HiddenDaemonProcess, self.__class__).daemon.fset(self, value)
        
        app.logger.info(f'RUNNER After')
        app.logger.info(f'RUNNER super().daemon: {super().daemon}')
        app.logger.info(f'RUNNER self.daemon: {self.daemon}')