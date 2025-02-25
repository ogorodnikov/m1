import os
import time
import tempfile
import traceback

from functools import wraps
from functools import partial

from logging import getLogger

from multiprocessing import Event
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor

from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import SamplerV2
from qiskit_ibm_runtime import QiskitRuntimeService

from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_multivector

from .algorithms.egcd import egcd
from .algorithms.bernvaz import bernvaz
from .algorithms.grover import grover
from .algorithms.grover_sudoku import grover_sudoku
from .algorithms.dj import dj
from .algorithms.simon import simon, simon_post_processing
from .algorithms.qft import qft
from .algorithms.qpe import qpe, qpe_post_processing
from .algorithms.teleport import teleport
from .algorithms.shor import shor, shor_post_processing
from .algorithms.counting import counting, counting_post_processing
from .algorithms.bb84 import bb84, bb84_post_processing
from .algorithms.qae import qae, qae_post_processing
from .algorithms.iqae import iqae, iqae_post_processing


class Runner:
    
    runner_functions = {'egcd': egcd,
                        'bernvaz': bernvaz,
                        'grover': grover,
                        'grover_sudoku': grover_sudoku,
                        'dj': dj,
                        'simon': simon,
                        'qft': qft,
                        'qpe': qpe,
                        'teleport': teleport,
                        'shor': shor,
                        'counting': counting,
                        'bb84': bb84,
                        'qae': qae,
                        'iqae': iqae,}
                   
    post_processing = {'simon': simon_post_processing,
                       'qpe': qpe_post_processing,
                       'shor': shor_post_processing,
                       'counting': counting_post_processing,
                       'bb84': bb84_post_processing,
                       'qae': qae_post_processing,
                       'iqae': iqae_post_processing,}
                       
    DEFAULT_TASK_TIMEOUT = 300
    SHOTS_COUNT = 1024

    def __init__(self, db):
        
        self.db = db
        
        self.logger = getLogger(__name__)

        self.queue_pool = None
        self.worker_active_flag = Event()
        
        self.qiskit_token = os.environ.get('QISKIT_TOKEN')
        self.task_timeout = int(os.environ.get('TASK_TIMEOUT'))
        self.backend_avoid_list = os.environ.get('BACKEND_AVOID_STRING').split()
        self.queue_workers_count = int(os.environ.get('QUEUE_WORKERS_PER_RUNNER'))

        self.simulator_backend = AerSimulator()

        QiskitRuntimeService.save_account(
            channel='ibm_quantum',
            token=self.qiskit_token,
            overwrite=True)

        try:
            self.ibmq_service = QiskitRuntimeService()

        except Exception as exception:
            self.log(f'RUNNER IBMQ Runtime Service exception: {exception}')
            self.ibmq_service = None
        
        self.log(f'RUNNER initiated: {self}')
        

    def log(self, message, task_id=None):
        
        self.logger.info(message)
        
        if task_id:
            self.db.update_task_attribute(task_id, 'logs', message, append=True)
        
    
    def start(self):

        self.worker_active_flag.set()
        
        self.queue_pool = ProcessPoolExecutor(max_workers=self.queue_workers_count,
                                              initializer=self.queue_worker_loop)

        dummy_starter_function = None

        # noinspection PyTypeChecker
        self.queue_pool.submit(dummy_starter_function)
        
        os.environ['RUNNER_STATE'] = 'Running'
        
        self.log(f'RUNNER started: {self}')
        

    def stop(self):
        
        self.worker_active_flag.clear()
        
        self.queue_pool.shutdown()
        
        os.environ['RUNNER_STATE'] = 'Stopped'
        
        self.log(f'RUNNER stopping: {self}')      
        
        
    def run_algorithm(self, algorithm_id, run_values):
        
        task_id = self.db.add_task(algorithm_id, run_values)
        
        self.log(f'RUNNER new_task: {task_id, algorithm_id, run_values}')
        
        return task_id

        
    def exception_decorator(wrapped_function):
        
        @wraps(wrapped_function)
        def wrapper(self, *args, **kwargs):

            try:
                return wrapped_function(self, *args, **kwargs)
                
            except Exception as exception:

                task_id = kwargs.get('task_id', None)
                
                stack_trace = traceback.format_exc()
                
                self.log(stack_trace, task_id)
                
                task_result = {'Result': {'Exception': repr(exception)}}
                
                if task_id:
                    
                    self.db.add_status_update(task_id, 'Failed', task_result)
                    
        return wrapper


    @exception_decorator
    def queue_worker_loop(self):
        
        self.log(f'RUNNER queue_worker started: {os.getpid()}')

        while self.worker_active_flag.is_set():

            time.sleep(1)
            next_task = self.get_next_task()

            if next_task:
                self.process_next_task(next_task, self.task_timeout)
            
        self.log(f'RUNNER queue_worker exiting: {os.getpid()}')


    @exception_decorator    
    def get_next_task(self):
        return self.db.get_next_task()
        
        
    @exception_decorator      
    def process_next_task(self, next_task, task_timeout=DEFAULT_TASK_TIMEOUT):
        
        self.log(f'RUNNER next_task: {next_task}')
        
        task_id = next_task['task_id']
        run_values = next_task['run_values']
        algorithm_id = next_task['algorithm_id']
        
        self.db.add_status_update(task_id, 'Running', '')
        
        task = {'task_id': int(task_id), 
                'algorithm_id': algorithm_id, 
                'run_values': run_values}
                  
        task_process_name = f"Process-task_{task_id}@{os.getpid()}"
        
        task_process = Process(target=self.run_task,
                               kwargs=task,
                               name=task_process_name,
                               daemon=False)
                                 
        task_process.start()
        task_process.join(task_timeout)
        
        if task_process.is_alive():

            task_process.terminate()
            task_process.join()
            
            raise TimeoutError(f"Task timeout: {task_timeout} seconds")
                

    @exception_decorator
    def run_task(self, **task):
        
        task_id = task.get('task_id')
        run_values = task.get('run_values')
        algorithm_id = task.get('algorithm_id')
        
        run_mode = run_values.get('run_mode')
        skip_statevector = run_values.get('skip_statevector')
        
        run_values['task_id'] = task_id
        result = None
        
        runner_function = Runner.runner_functions[algorithm_id]
        
        task_log_callback = partial(self.log, task_id=task_id)

        self.log(f'RUNNER run_mode: {run_mode}')
        self.log(f'RUNNER run_values: {run_values}')
        self.log(f'RUNNER runner_function: {runner_function}')


        if self.ibmq_service is None and run_mode == 'quantum_device':

            self.log(f'RUNNER no IBMQ Service - falling back to Simulator')

            run_mode = 'simulator'


        if run_mode == 'classical':
            
            run_result = runner_function(run_values, task_log_callback)
            
            result = {'Result': run_result}

        
        elif run_mode == 'simulator':
            
            circuit = runner_function(run_values, task_log_callback)
            
            self.log(f'RUNNER backend: {self.simulator_backend}', task_id)
            
            run_result = self.execute_task(task_id, circuit, self.simulator_backend)
            counts = run_result.get_counts()

            if not skip_statevector:
                self.handle_statevector(circuit, task_id)

            # self.log(f'RUNNER run_result: {run_result}', task_id)
            # self.log(f'RUNNER counts:', task_id)
            # [self.log(f'{state}: {count}', task_id) for state, count in sorted(counts.items())]
            
            result = {'Counts': counts}
            
            
        elif run_mode == 'quantum_device':

            circuit = runner_function(run_values, task_log_callback)
            qubit_count = circuit.num_qubits       
                
            self.log(f'RUNNER ibmq_service: {self.ibmq_service}', task_id)
            
            backend = self.get_least_busy_backend(self.ibmq_service,
                                                  qubit_count,
                                                  self.backend_avoid_list)
            
            self.log(f'RUNNER backend: {backend}', task_id)
            
            run_result = self.execute_task(task_id, circuit, backend)
            counts = run_result.get_counts()

            self.log(f'RUNNER run_result: {run_result}', task_id)
            self.log(f'RUNNER counts:', task_id)
            [self.log(f'{state}: {count}', task_id) for state, count in sorted(counts.items())]
            
            result = {'Counts': counts}
            
            
        if algorithm_id in Runner.post_processing:
            
            post_processing_function = Runner.post_processing[algorithm_id]

            run_data = {'Result': result, 'Run Values': run_values}
            
            self.log(f'RUNNER run_data: {run_data}', task_id)
            
            post_processing_result = post_processing_function(run_data, 
                                                              task_log_callback)
            
            result = {'Result': post_processing_result}
            
            
        self.log(f'RUNNER result: {result}', task_id)

        self.db.add_status_update(task_id, 'Done', result)
        

    def execute_task(self, task_id, circuit, backend):

        transpiled_circuit = transpile(circuit, backend)

        transpiled_circuit_printout = transpiled_circuit.draw(
            fold=-1, idle_wires=False)

        self.log(f'RUNNER transpiled circuit: \n{transpiled_circuit_printout}\n', task_id)

        sampler = SamplerV2(mode=backend)

        pub = [transpiled_circuit, None, SHOTS_COUNT]

        job = sampler.run([pub])

        self.monitor_job(job, task_id)

        first_pub_result = job.result()[0]

        first_register, first_result = dict(first_pub_result.data).popitem()

        return first_result
        
        
    def monitor_job(self, job, task_id, interval=1, max_interval=8):
        
        self.log(f'RUNNER job_id: {job.job_id()}', task_id)

        while True:

            if hasattr(job.status(), 'name'):
                status = job.status().name
            else:
                status = job.status()

            if status == 'QUEUED':
                position = job.metrics()['position_in_queue']
                status += f", position in queue: {position}"
                
            self.log(f"RUNNER job status: {status}", task_id)
            
            if status in ['QUEUED', 'RUNNING']:
                interval = min(interval * 2, max_interval)
            
            if status in ['DONE', 'CANCELLED', 'ERROR']:
                break

            time.sleep(interval)

        if hasattr(job, 'metrics'):

            self.log(f'RUNNER job metrics: {job.metrics()}', task_id)
            
            
    def handle_statevector(self, circuit, task_id):
        
        state_circuit = circuit.copy()
        state_circuit.remove_final_measurements()

        statevector = Statevector(state_circuit)

        self.log(f'RUNNER statevector:', task_id)
            
        for state_index, probability_amplitude in enumerate(statevector):
            
            if not probability_amplitude:
                continue
                
            state = f'{state_index:0{circuit.num_qubits}b}'
                
            self.log(f'{state}: {probability_amplitude}', task_id)

        self.plot_statevector_figure(statevector, task_id)
        
    
    def plot_statevector_figure(self, statevector, task_id):
        
        self.log(f'RUNNER plot_statevector_figure', task_id)
        
        figure = plot_bloch_multivector(statevector)
        
        figure_filename = f'bloch_multivector_task_{task_id}.png'

        temporary_folder = tempfile.gettempdir()
        
        temporary_figure_path = os.path.join(temporary_folder, figure_filename)
        s3_figure_path = os.path.join('figures', figure_filename)
        
        figure.savefig(temporary_figure_path, transparent=True, bbox_inches='tight')
        
        self.db.move_figure_to_s3(from_path=temporary_figure_path, 
                                  to_path=s3_figure_path)


    @staticmethod
    def get_least_busy_backend(ibmq_service, qubit_count, backend_avoid_list):
    
        backend_filter = lambda backend: (not backend.configuration().simulator 
                                          and backend.configuration().n_qubits >= qubit_count
                                          and backend.status().operational
                                          and backend.name not in backend_avoid_list)

        filtered_backend = ibmq_service.least_busy(filters=backend_filter)

        return filtered_backend
