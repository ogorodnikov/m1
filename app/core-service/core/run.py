import time
import traceback

from os import getpid, _exit
from functools import partial
from multiprocessing import Process, Event, Queue, Manager, Pool

from qiskit import IBMQ, Aer, execute
from qiskit.providers.ibmq import least_busy
from qiskit.visualization import plot_bloch_multivector
from qiskit.tools.monitor import backend_overview, job_monitor

from core import app

from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz
from core.algorithms.grover import grover
from core.algorithms.grover_sudoku import grover_sudoku
from core.algorithms.dj import dj
from core.algorithms.simon import simon, simon_post_processing
from core.algorithms.qft import qft
from core.algorithms.qpe import qpe


class Runner():
    
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
    
    PLOT_STATEVECTOR_TIMEOUT = 5
    TASK_TIMEOUT = 3
    
    
    def __init__(self, *args, **kwargs):
        
        self.task_process_count = app.config.get('CPU_COUNT', 1)
        self.task_rollover_size = app.config.get('TASK_ROLLOVER_SIZE', 100)
        
        ### Test
        # self.task_process_count = 2
        
        self.task_id = 0
        
        self.task_queue = Queue()
        self.task_results_queue = Queue()
        
        self.manager = Manager()
        
        self.logs = manager.dict()
        self.tasks = manager.dict()
        
        self.worker_active_flag = Event()
        self.worker_active_flag.set()
        
        self.start_task_worker_processes()
        
        
        self.tasks_pool = Pool(processes=task_process_count)
        

        app.logger.info(f'RUNNER initiated: {self}')
        
        
    def task_log(task_id, message):

        app.logger.info(f'{message}')
        
        logs[task_id] += [message]




    def run_algorithm(self, algorithm_id, run_values):
        
        self.task_id = self.task_id % self.task_rollover_size + 1
        
        new_task = (self.task_id, algorithm_id, run_values)
        
        self.task_queue.put(new_task)
        
        new_task_record = {'algorithm_id': algorithm_id,
                           'run_values': run_values,
                           'status': 'Queued'}
                           
        self.tasks[task_id] = self.manager.dict(new_task_record)
        self.logs[task_id] = self.manager.list()
        
        app.logger.info(f'RUNNER task_id: {task_id}')
        app.logger.info(f'RUNNER new_task: {new_task}')
        app.logger.info(f'RUNNER task_queue: {task_queue}')
        app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
        
        return self.task_id
        
    
    def start_task_worker_processes(self):
        
        self.task_worker_processes = []
        
        for i in range(self.task_process_count):
        
            task_worker_process = Process(
                                      target=self.task_worker,
                                      args=(self.task_queue, self.task_results_queue, self.worker_active_flag),
                                      daemon=True)
                                                  
            task_worker_process.start()
            
            self.task_worker_processes.append(task_worker_process)
            
    
    def task_worker(self, task_queue, task_results_queue, worker_active_flag):
        
        app.logger.info(f'RUNNER task_worker started: {getpid()}')
        
        while True:
            
            time.sleep(1)
            
            if self.worker_active_flag.is_set() and not self.task_queue.empty():
                
                pop_task = self.task_queue.get()
                
                task_id, algorithm_id, run_values = pop_task
                
                self.task_results_queue.put((task_id, '', 'Running'))
                
                app.logger.info(f'RUNNER pop_task: {pop_task}')
                app.logger.info(f'RUNNER task_queue.qsize: {self.task_queue.qsize()}')
                
                try:
                    
                    result = self.task_runner(task_id, algorithm_id, run_values)
                    status = 'Done'
                    
                except Exception as exception:
                    
                    error_message = traceback.format_exc()
                    self.task_log(task_id, error_message)
                    
                    result = None
                    status = 'Failed'
                
                task_results_queue.put((task_id, result, status))
    
                self.task_log(task_id, f'RUNNER Result: {result}')
                self.task_log(task_id, f'RUNNER Status: {status}')
                
                app.logger.info(f'RUNNER task_results_queue.qsize: {self.task_results_queue.qsize()}')
                app.logger.info(f'RUNNER len(tasks): {len(self.tasks)}')
            
    
    def task_runner(self, task_id, algorithm_id, run_values_multidict):
        
        run_values = dict(run_values_multidict)
        run_values['task_id'] = task_id
        
        runner_function = Runner.runner_functions[algorithm_id]
        
        run_mode = run_values.get('run_mode')
        
        app.logger.info(f'RUNNER run_mode: {run_mode}')
        app.logger.info(f'RUNNER run_values: {run_values}')
        app.logger.info(f'RUNNER runner_function: {runner_function}') 
        
        task_log_callback = partial(self.task_log, task_id)
        
        
        if run_mode == 'classical':
            
            return runner_function(run_values, task_log_callback)
            
        
        elif run_mode == 'simulator':
            
            circuit = runner_function(run_values, task_log_callback)
            qubit_count = circuit.num_qubits
            
            backend = Aer.get_backend('qasm_simulator')
            
            circuit.save_statevector()
            
            result = execute_task(task_id, circuit, backend)
            
            # self.task_log(task_id, f'RUNNER result: {result}')
    
            counts = result.get_counts()
            
            # self.task_log(task_id, f'RUNNER counts: {counts}')
            
            statevector = result.get_statevector(decimals=3)
            
            plot_statevector_figure(task_id, statevector)
    
            self.task_log(task_id, f'RUNNER statevector:')
            
            for state_index, probability_amplitude in enumerate(statevector):
                
                if not probability_amplitude:
                    continue
                
                state = f'{state_index:0{qubit_count}b}'
                
                self.task_log(task_id, f'{state}: {probability_amplitude}')
            
            
        elif run_mode == 'quantum_device':
        
            qiskit_token = app.config.get('QISKIT_TOKEN')
            IBMQ.save_account(qiskit_token)
            
            if not IBMQ.active_account():
                IBMQ.load_account()
                
            ibmq_provider = IBMQ.get_provider()
            
            self.task_log(task_id, f'RUNNER ibmq_provider: {ibmq_provider}')
            self.task_log(task_id, f'RUNNER ibmq_provider.backends(): {ibmq_provider.backends()}')
            
            circuit = runner_function(run_values, task_log_callback)
            qubit_count = circuit.num_qubits        
    
            backend = get_least_busy_backend(ibmq_provider, qubit_count)
            
            result = execute_task(task_id, circuit, backend)
            counts = result.get_counts()
            
            
        if algorithm_id not in Runner.post_processing:
            task_result = {'Counts': counts}
            
        else:
            task_result = Runner.post_processing[algorithm_id](counts, task_log_callback)
        
        self.task_log(task_id, f'RUNNER task_result: {task_result}')
    
        return task_result
        
        
    def execute_task(self, task_id, circuit, backend):
        
        self.task_log(task_id, f'RUNNER backend: {backend}')
        
        job = execute(circuit, backend=backend, shots=1024)
        
        job_monitor(job, interval=0.5)
        
        result = job.result()
        counts = result.get_counts()
        
        self.task_log(task_id, f'RUNNER counts:')
        [self.task_log(task_id, f'{state}: {count}') for state, count in sorted(counts.items())]
        
        return result
        
    
    def get_task_results(self):
        
        while not self.task_results_queue.empty():
            
            task_result = self.task_results_queue.get()
            
            task_id, result, status = task_result
            
            self.tasks[task_id]['result'] = result            
            self.tasks[task_id]['status'] = status
            
            if status == 'Running':
                continue
            
            yield task_result
    
        
    def get_least_busy_backend(self, provider, qubit_count):
    
        backend_filter = lambda backend: (not backend.configuration().simulator 
                                          and backend.configuration().n_qubits >= qubit_count
                                          and backend.status().operational==True)
            
        least_busy_backend = least_busy(provider.backends(filters=backend_filter))
        
        return least_busy_backend
        
    
    def plot_statevector_figure(self, task_id, statevector):
            
        figure = plot_bloch_multivector(statevector)
        
        self.task_log(task_id, f'RUNNER figure: {figure}')        
    
        figure_path = app.static_folder + f'/figures/bloch_multivector_task_{task_id}.png'
                    
        figure.savefig(figure_path, transparent=True, bbox_inches='tight')
        
        
    def terminate_application(self, message):
        
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