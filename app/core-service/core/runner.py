import os
import time
import tempfile
import traceback

from logging import getLogger
from functools import partial

from multiprocessing import Event
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor

from qiskit import Aer
from qiskit import IBMQ
from qiskit import execute
from qiskit.providers.ibmq import least_busy
from qiskit.visualization import plot_bloch_multivector
from qiskit.tools.monitor import backend_overview, job_monitor

from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz
from core.algorithms.grover import grover
from core.algorithms.grover_sudoku import grover_sudoku
from core.algorithms.dj import dj
from core.algorithms.simon import simon, simon_post_processing
from core.algorithms.qft import qft
from core.algorithms.qpe import qpe, qpe_post_processing
from core.algorithms.shor import shor


class Runner():
    
    runner_functions = {'egcd': egcd,
                        'bernvaz': bernvaz,
                        'grover': grover,
                        'grover_sudoku': grover_sudoku,
                        'dj': dj,
                        'simon': simon,
                        'qft': qft,
                        'qpe': qpe,
                        'shor': shor}
                   
    post_processing = {'simon': simon_post_processing,
                       'qpe': qpe_post_processing}

    def __init__(self, db, *args, **kwargs):
        
        self.db = db
        
        self.logger = getLogger(__name__)

        self.worker_active_flag = Event()
        
        self.qiskit_token = os.environ.get('QISKIT_TOKEN')
        self.task_timeout = os.environ.get('TASK_TIMEOUT')
        self.backend_avoid_list = os.environ.get('BACKEND_AVOID_STRING').split()
        self.queue_workers_count = os.environ.get('QUEUE_WORKERS_PER_RUNNER')
        
        IBMQ.enable_account(self.qiskit_token)
        
        self.log(f'RUNNER initiated: {self}')
        

    def log(self, message, task_id=None):
        
        self.logger.info(message)
        
        if task_id:
            self.db.update_task_attribute(task_id, 'logs', message, append=True)
        
    
    def start(self):
        
        self.worker_active_flag.set()
        
        self.queue_pool = ProcessPoolExecutor(max_workers=self.queue_workers_count,
                                         initializer=self.queue_worker)
        
        worker_future = self.queue_pool.submit(self.queue_worker)
        
        os.environ['RUNNER_STATE'] = 'Running'
        
        self.log(f'RUNNER started: {self}')
        

    def stop(self):
        
        self.worker_active_flag.clear()
        
        self.queue_pool.shutdown()
        
        os.environ['RUNNER_STATE'] = 'Stopped'
        
        self.log(f'RUNNER stopped: {self}')      
        
        
    def run_algorithm(self, algorithm_id, run_values):
        
        task_id = self.db.add_task(algorithm_id, run_values)
        
        self.log(f'RUNNER new_task: {task_id, algorithm_id, run_values}')
        
        return task_id
        
    
    def exception_decorator(function):
        
        def wrapper(self, *args, **kwargs):

            try:
                return function(self, *args, **kwargs)
                
            except Exception as exception:

                task_id = kwargs.get('task_id', None)
                
                stack_trace = traceback.format_exc()
                
                self.log(stack_trace, task_id)
                
                task_result = {'Exception': repr(exception)}
                
                if task_id:
                    
                    self.db.add_status_update(task_id, 'Failed', task_result)

        return wrapper


    @exception_decorator    
    def get_next_task(self):
        
        return self.db.get_next_task()
        
        
    @exception_decorator
    def queue_worker(self):
        
        self.log(f'RUNNER queue_worker started: {os.getpid()}')

        while self.worker_active_flag.is_set():
            
            time.sleep(1)

            next_task = self.get_next_task()

            if next_task:
  
                self.queue_worker_loop(next_task=next_task)
            
        self.log(f'RUNNER queue_worker exiting: {os.getpid()}')
        
        
    @exception_decorator      
    def queue_worker_loop(self, next_task):
        
        self.log(f'RUNNER next_task: {next_task}')
        
        task_id = next_task['task_id']
        run_values = next_task['run_values']
        algorithm_id = next_task['algorithm_id']
        
        self.db.add_status_update(task_id, 'Running', '')
        
        kwargs = {'task_id': int(task_id), 
                  'algorithm_id': algorithm_id, 
                  'run_values': run_values}
        
        task_process = Process(target=self.run_task,
                               kwargs=kwargs,
                               name=f"Task-process-{os.getpid()}",
                               daemon=False)
                                 
        task_process.start()
        task_process.join(self.task_timeout)
        
        if task_process.is_alive():

            task_process.terminate()
            task_process.join()
            
            raise TimeoutError(f"Task timeout: {self.task_timeout} seconds")
                

    @exception_decorator
    def run_task(self, **kwargs):
        
        task_id = kwargs.get('task_id')
        run_values = kwargs.get('run_values')
        algorithm_id = kwargs.get('algorithm_id')
        
        run_mode = run_values.get('run_mode')
        run_values['task_id'] = task_id
        
        runner_function = Runner.runner_functions[algorithm_id]
        
        task_log_callback = partial(self.log, task_id=task_id)
        
        self.log(f'RUNNER run_mode: {run_mode}')
        self.log(f'RUNNER run_values: {run_values}')
        self.log(f'RUNNER runner_function: {runner_function}') 
        
        
        if run_mode == 'classical':
            
            function_result = runner_function(run_values, task_log_callback)
            
            result = {'Result': function_result}

        
        elif run_mode == 'simulator':
            
            circuit = runner_function(run_values, task_log_callback)
            qubit_count = circuit.num_qubits
            
            backend = Aer.get_backend('qasm_simulator')
            
            self.log(f'RUNNER backend: {backend}', task_id)
            
            circuit.save_statevector()
            
            run_result = self.execute_task(task_id, circuit, backend)
            counts = run_result.get_counts()
            
            self.handle_statevector(run_result, qubit_count, task_id)

            self.log(f'RUNNER run_result: {run_result}', task_id)
            self.log(f'RUNNER counts:', task_id)
            [self.log(f'{state}: {count}', task_id) for state, count in sorted(counts.items())]
            
            result = {'Counts': counts}
            
            
        elif run_mode == 'quantum_device':

            circuit = runner_function(run_values, task_log_callback)
            qubit_count = circuit.num_qubits       
                
            ibmq_provider = IBMQ.get_provider()
            
            self.log(f'RUNNER ibmq_provider: {ibmq_provider}', task_id)
            
            backend = self.get_least_busy_backend(ibmq_provider, qubit_count)
            
            self.log(f'RUNNER backend: {backend}', task_id)
            
            run_result = self.execute_task(task_id, circuit, backend)
            counts = run_result.get_counts()

            self.log(f'RUNNER run_result: {run_result}', task_id)
            self.log(f'RUNNER counts:', task_id)
            [self.log(f'{state}: {count}', task_id) for state, count in sorted(counts.items())]
            
            result = {'Counts': counts}
            
            
        if algorithm_id in Runner.post_processing:
            
            post_processing_function = Runner.post_processing[algorithm_id]
            
            post_processing_result = post_processing_function(counts, task_log_callback)
            
            result = {'Result': post_processing_result}
            
        
        self.log(f'RUNNER result: {result}', task_id)

        self.db.add_status_update(task_id, 'Done', result)
        

    def execute_task(self, task_id, circuit, backend):
        
        job = execute(circuit, backend=backend, shots=1024)
        
        self.monitor_job(job, task_id)

        return job.result()
        
        
    def monitor_job(self, job, task_id, interval=1):
        
        max_interval = 4
        
        while True:
            
            status = job.status().name
            status_update = f"job status: {status}"
            
            if status == 'QUEUED':
                position = job.queue_position()
                status_update += f" at position {position}"
                
            self.log(f'RUNNER {status_update}', task_id)
            
            if status in ('QUEUED', 'RUNNING'):
                interval = min(interval*2, max_interval)
            
            if status in ('DONE', 'CANCELLED', 'ERROR'):
                break
            
            time.sleep(interval)
            
            
    def handle_statevector(self, run_result, qubit_count, task_id):
        
        statevector = run_result.get_statevector(decimals=3)
            
        self.log(f'RUNNER statevector:', task_id)
            
        for state_index, probability_amplitude in enumerate(statevector):
                
            if not probability_amplitude:
                continue
                
            state = f'{state_index:0{qubit_count}b}'
                
            self.log(f'{state}: {probability_amplitude}', task_id)
                
        self.plot_statevector_figure(task_id, statevector)
        
    
    def get_least_busy_backend(self, provider, qubit_count):
    
        backend_filter = lambda backend: (not backend.configuration().simulator 
                                          and backend.configuration().n_qubits >= qubit_count
                                          and backend.status().operational==True
                                          and backend.name() not in self.backend_avoid_list)
                                          
        filtered_backends = provider.backends(filters=backend_filter)
        
        if filtered_backends:
            return least_busy(filtered_backends)
        
        else:
            raise ValueError(f"No IBMQ backends match specified qubit_count: {qubit_count}")
        
    
    def plot_statevector_figure(self, task_id, statevector):
        
        figure = plot_bloch_multivector(statevector)
    
        figure_filename = f'bloch_multivector_task_{task_id}.png'
        
        temporary_folder = tempfile.gettempdir()
        
        temporary_figure_path = os.path.join(temporary_folder, figure_filename)
        s3_figure_path = os.path.join('figures', figure_filename)
        
        figure.savefig(temporary_figure_path, transparent=True, bbox_inches='tight')
        
        self.db.move_figure_to_s3(from_path=temporary_figure_path, 
                                  to_path=s3_figure_path)
        
        self.log(f'RUNNER statevector figure: {figure}', task_id)