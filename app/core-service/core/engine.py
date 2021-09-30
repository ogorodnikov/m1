import time
import traceback

from os import getpid, _exit
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process, Event, Manager

from qiskit import IBMQ, Aer, execute
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
                        'shor': shor
                       }
                   
    post_processing = {'simon': simon_post_processing,
                       'qpe': qpe_post_processing
                      }

    def __init__(self, app, *args, **kwargs):
        
        self.app = app
        
        self.db = self.app.config.get('DB')
        self.qiskit_token = self.app.config.get('QISKIT_TOKEN')
        self.task_timeout = self.app.config.get('TASK_TIMEOUT')
        self.backend_avoid_list = self.app.config.get('BACKEND_AVOID_LIST')
        self.queue_workers_count = self.app.config.get('QUEUE_WORKERS_PER_RUNNER')
        
        self.static_folder = self.app.static_folder

        self.manager = Manager()
        self.worker_active_flag = Event()
        
        self.app.config['RUNNER'] = self
        self.app.config['RUNNER_STATE'] = 'Stopped'
        
        self.log(f'RUNNER initiated: {self}')
        
        
    def log(self,message):
        self.app.logger.info(message)
        

    def task_log(self, task_id, message):
        self.log(message)
        self.db.update_task_attribute(task_id, 'logs', message, append=True)
        
    
    def start(self):

        self.worker_active_flag.set()
        
        self.queue_pool = ProcessPoolExecutor(max_workers=self.queue_workers_count,
                                         initializer=self.queue_worker)
        
        worker_future = self.queue_pool.submit(self.queue_worker)
        
        self.app.config['RUNNER_STATE'] = 'Started'
        self.log(f'RUNNER started: {self}')
        
        # worker_future = queue_pool.submit(pow, 12, 133)

        # canceled = worker_future.cancel()
                
        # time.sleep(3)
        
        # result = worker_future.result(timeout=3)
        
        # self.log(f'RUNNER worker_future: {worker_future}')
        # self.log(f'RUNNER result: {result}')
        
        # self.log(f'RUNNER worker_future.done(): {worker_future.done()}')
        # self.log(f'RUNNER canceled: {canceled}')
        

    def stop(self):
        
        self.worker_active_flag.clear()
        
        self.queue_pool.shutdown()
        
        self.app.config['RUNNER_STATE'] = 'Stopped'
        self.log(f'RUNNER stopped: {self}')      
        
        
    def run_algorithm(self, algorithm_id, run_values):
        
        task_id = self.db.add_task(algorithm_id, run_values)
        
        self.log(f'RUNNER new_task: {task_id, algorithm_id, run_values}')
        
        return task_id
        
    
    # def exception_decorator(function):
        
    #     def wrapper(self, *args, **kwargs):
            
    #         try:
    #             function(self, *args, **kwargs)
                
    #         except Exception as exception:
                
    #             stack_trace = traceback.format_exc()
                
    #             self.log(f'RUNNER exception args: {args}')
    #             self.log(f'RUNNER exception kwargs: {kwargs}')

    #             result = kwargs.get('result')                
    #             task_id = kwargs.get('task_id')
                
    #             if task_id:
                
    #                 self.task_log(task_id, stack_trace)
                    
    #                 result.update({'Status': 'Failed',
    #                               'Result': {'Exception': repr(exception)},
    #                               'Stack trace': stack_trace})

    #                 raise exception
                    
    #             else:
                    
    #                 self.log(f'RUNNER queue_worker exception: {stack_trace}')
        
    #     return wrapper
        
        
    # @exception_decorator
    def queue_worker(self):
        
        self.log(f'RUNNER queue_worker started: {getpid()}')
        
        while self.worker_active_flag.is_set():
                
            try:
                
                time.sleep(1)
                
                # self.log(f'RUNNER queue_worker loop: {getpid()}')
                
                next_task = self.db.get_next_task()
                
                if not next_task:
                    continue
                
                self.log(f'RUNNER next_task: {next_task}')
                
                task_id = next_task['task_id']
                run_values = next_task['run_values']
                algorithm_id = next_task['algorithm_id']
                
                self.db.add_status_update(task_id, 'Running', '')
                
                result = self.manager.dict()
    
                kwargs = {'task_id': int(task_id), 
                          'algorithm_id': algorithm_id, 
                          'run_values': run_values, 
                          'result': result}
                
                task_process = Process(target=self.run_task,
                                    #   args=(task_id, algorithm_id, run_values, result),
                                       kwargs=kwargs,
                                       name=f"Task-process-{getpid()}",
                                       daemon=False)
                                         
                task_process.start()
                task_process.join(self.task_timeout)
                
                if task_process.is_alive():
    
                    task_process.terminate()
                    task_process.join()
                    
                    raise TimeoutError(f"Task timeout: {self.task_timeout} seconds")
                
                # task_result = result.get('Result')
                # task_status = result.get('Status')
       
                # self.task_log(task_id, f'RUNNER Result: {task_result}')
                # self.task_log(task_id, f'RUNNER Status: {task_status}')
    
                # print(f'RUNNER queue_worker status update: {task_id, task_status, task_result}')
                
                # self.db.add_status_update(task_id, task_status, task_result)
                
            except Exception as exception:
                    
                stack_trace = traceback.format_exc()
                
                self.task_log(task_id, stack_trace)
                
                self.db.add_status_update(task_id, 'Failed', {'Exception': repr(exception)})

        self.log(f'RUNNER queue_worker exiting: {getpid()}')
        

    # @exception_decorator
    def run_task(self, **kwargs):
        
        result = kwargs.get('result')        
        task_id = kwargs.get('task_id')
        run_values = kwargs.get('run_values')
        algorithm_id = kwargs.get('algorithm_id')
        
        run_mode = run_values.get('run_mode')
        run_values['task_id'] = task_id
        
        runner_function = Runner.runner_functions[algorithm_id]
        
        task_log_callback = partial(self.task_log, task_id)
        
        self.log(f'RUNNER run_mode: {run_mode}')
        self.log(f'RUNNER run_values: {run_values}')
        self.log(f'RUNNER runner_function: {runner_function}') 
        
        
        if run_mode == 'classical':
            
            function_result = runner_function(run_values, task_log_callback)
            
            task_result = {'Result': function_result}

        
        elif run_mode == 'simulator':
            
            circuit = runner_function(run_values, task_log_callback)
            qubit_count = circuit.num_qubits
            
            backend = Aer.get_backend('qasm_simulator')
            
            circuit.save_statevector()
            
            run_result = self.execute_task(task_id, circuit, backend)

            counts = run_result.get_counts()
            
            statevector = run_result.get_statevector(decimals=3)
            
            self.task_log(task_id, f'RUNNER counts: {counts}')
            self.task_log(task_id, f'RUNNER statevector:')
            
            for state_index, probability_amplitude in enumerate(statevector):
                
                if not probability_amplitude:
                    continue
                
                state = f'{state_index:0{qubit_count}b}'
                
                self.task_log(task_id, f'{state}: {probability_amplitude}')
                
            self.plot_statevector_figure(task_id, statevector)
                
            task_result = {'Result': {'Counts': counts}}
            
            
        elif run_mode == 'quantum_device':

            circuit = runner_function(run_values, task_log_callback)
            qubit_count = circuit.num_qubits       
            
            IBMQ.save_account(self.qiskit_token)
            
            if not IBMQ.active_account():
                IBMQ.load_account()
                
            ibmq_provider = IBMQ.get_provider()
            
            backend = self.get_least_busy_backend(ibmq_provider, qubit_count)
            
            run_result = self.execute_task(task_id, circuit, backend)
            counts = run_result.get_counts()
            
            task_result = {'Result': {'Counts': counts}}
            
            
        if algorithm_id in Runner.post_processing:
            
            post_processing_function = Runner.post_processing[algorithm_id]
            
            post_processing_result = post_processing_function(counts, task_log_callback)
            
            task_result = {'Result': post_processing_result}
            

        # result.update({'Status': 'Done'})
        
        # result.update(task_result)
        
        self.db.add_status_update(task_id, 'Done', task_result)


    def execute_task(self, task_id, circuit, backend):
        
        self.task_log(task_id, f'RUNNER backend: {backend}')
        
        job = execute(circuit, backend=backend, shots=1024)
        
        job_monitor(job, interval=0.5)
        
        result = job.result()
        counts = result.get_counts()
        
        self.task_log(task_id, f'RUNNER counts:')
        [self.task_log(task_id, f'{state}: {count}') for state, count in sorted(counts.items())]
        
        return result
        
    
    def get_least_busy_backend(self, provider, qubit_count):
    
        backend_filter = lambda backend: (not backend.configuration().simulator 
                                          and backend.configuration().n_qubits >= qubit_count
                                          and backend.status().operational==True
                                          and backend.name() not in self.backend_avoid_list)
            
        least_busy_backend = least_busy(provider.backends(filters=backend_filter))
        
        return least_busy_backend
        
    
    def plot_statevector_figure(self, task_id, statevector):
            
        figure = plot_bloch_multivector(statevector)
    
        figure_path = self.static_folder + f'/figures/bloch_multivector_task_{task_id}.png'
                    
        figure.savefig(figure_path, transparent=True, bbox_inches='tight')
        
        self.task_log(task_id, f'RUNNER statevector figure: {figure}')    

        
    def reset_application(self):
        
        self.log(f'RUNNER reset_application')
        
        _exit(0)