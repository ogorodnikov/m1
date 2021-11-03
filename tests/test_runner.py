import os
import time
import pytest
import decorator

from _pytest.monkeypatch import MonkeyPatch

from core.runner import Runner
from core.dynamo import Dynamo


from threading import Thread, Timer
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor


from qiskit import IBMQ


@pytest.mark.slow
def test_start_stop(runner):
    
    runner.start()
    assert os.environ.get('RUNNER_STATE') == 'Running'
    
    runner.stop()
    assert os.environ.get('RUNNER_STATE') == 'Stopped'


def test_log(runner):
    runner.log(message='test', task_id=1)
    

def test_run_algorithm(runner):
    runner.run_algorithm(None, None)
    

def test_exception_decorator(runner):
    
    def raise_exception():
        raise UserWarning
        
    decorated_raise_exception = Runner.exception_decorator(raise_exception)
    
    decorated_raise_exception(runner, task_id='test_task_id')
        

def test_queue_worker_loop(runner, undecorate):
    
    runner.worker_active_flag.set()
    
    def clear_worker_active_flag():
        runner.worker_active_flag.clear()
    
    test_timer = Timer(interval=1, function=clear_worker_active_flag)
    test_timer.start()
    
    runner.queue_worker_loop()
    
    
def test_get_next_task(runner, undecorate):
    runner.get_next_task()
    

def test_process_next_task(runner, get_test_task, undecorate):
    
    test_task = get_test_task()
    
    runner.process_next_task(test_task)


def test_process_next_task_timeout(runner, get_test_task, undecorate):
    
    test_task = get_test_task()
    
    with pytest.raises(TimeoutError, match=r"Task timeout: 0 seconds"):
        runner.process_next_task(test_task, task_timeout=0)
        

def test_run_task_classical(runner, undecorate):

    test_task = {'task_id': '1', 
                 'run_values': {
                     'run_mode': 'classical', 'a': '345', 'b': '455244237'},
                 'algorithm_id': 'egcd'}

    runner.run_task(**test_task)
    

def test_run_task_simulator(runner, mock_runner_functions, mock_ibmq_backend, undecorate):

    test_task = {'task_id': '1', 
                 'run_values': {'run_mode': 'simulator', 'secret': '1010'},
                 'algorithm_id': 'test_algorithm'}
                 
    runner.run_task(**test_task)


def test_run_task_quantum(runner, mock_runner_functions, mock_ibmq_backend, undecorate):
    
    test_task = {'task_id': '1', 
                 'run_values': {'run_mode': 'quantum_device', 'secret': '1010'},
                 'algorithm_id': 'test_algorithm'}

    runner.run_task(**test_task)
    

# def test_run_task_post_processing(runner, mock_runner_functions, mock_post_processing, 
#                                   mock_ibmq_backend, undecorate):
    
#     test_task = {'task_id': '1', 
#                  'run_values': {'run_mode': 'simulator', 'secret': '1010'},
#                  'algorithm_id': 'bernvaz'}

#     runner.run_task(**test_task)   
    
    
###   Fixtures   ###

@pytest.fixture(scope="module")
def runner():

    db = Dynamo()    
    runner = Runner(db)
    
    yield runner

@pytest.fixture(scope="module")
def monkeypatch_module(request):
    
    monkeypatch_module = MonkeyPatch()
    yield monkeypatch_module
    monkeypatch_module.undo()
    

@pytest.fixture(scope="module")
def get_test_task():
    
    def get_test_task_wrapper(*args, **kwargs):
    
        test_task = {'task_id': '1', 
                     'run_values': {
                         'run_mode': 'classical', 'a': '345', 'b': '455244237'},
                     'algorithm_id': 'egcd'}
        
        return test_task
    
    yield get_test_task_wrapper
    

@pytest.fixture(autouse=True, scope="module")
def mocks(monkeypatch_module, get_test_task):
    
    def stub(*args, **kwargs):
        pass
    
    monkeypatch_module.setattr(Dynamo, "add_task", stub)
    monkeypatch_module.setattr(Dynamo, "add_status_update", stub)
    monkeypatch_module.setattr(Dynamo, "update_task_attribute", stub)
    
    monkeypatch_module.setattr(Dynamo, "get_next_task", get_test_task)
    

@pytest.fixture
def undecorate(runner, monkeypatch):
    
    undecorated_queue_worker_loop = runner.queue_worker_loop.__wrapped__
    undecorated_get_next_task = runner.get_next_task.__wrapped__
    undecorated_process_next_task = runner.process_next_task.__wrapped__
    undecorated_run_task = runner.run_task.__wrapped__
    
    monkeypatch.setattr(Runner, "queue_worker_loop", undecorated_queue_worker_loop)
    monkeypatch.setattr(Runner, "get_next_task", undecorated_get_next_task)
    monkeypatch.setattr(Runner, "process_next_task", undecorated_process_next_task)
    monkeypatch.setattr(Runner, "run_task", undecorated_run_task)
    

@pytest.fixture
def set_zero_task_timeout(monkeypatch):
    
    monkeypatch.setenv("TASK_TIMEOUT", '0')


@pytest.fixture
def mock_runner_functions(runner, monkeypatch):
    
    def get_dummy_circuit(*args, **kwargs):
        
        class DummyCircuit:
            
            num_qubits = None
            
            def save_statevector(self):
                pass
                
        return DummyCircuit()
    
    monkeypatch.setitem(runner.runner_functions, "test_algorithm", get_dummy_circuit)
    
    # runner_functions = {'egcd': egcd,
    #                     'bernvaz': bernvaz,
    #                     'grover': grover,
    #                     'grover_sudoku': grover_sudoku,
    #                     'dj': dj,
    #                     'simon': simon,
    #                     'qft': qft,
    #                     'qpe': qpe,
    #                     'shor': shor}
                   
    # post_processing = {'simon': simon_post_processing,
    #                   'qpe': qpe_post_processing}
    
    
@pytest.fixture
def mock_ibmq_backend(monkeypatch):
    
    def get_dummy_run_result(*args, **kwargs):
        
        class DummyRunResult:
            def get_counts(self):
                return dict()
                
        return DummyRunResult()
        
    def get_none(*args, **kwargs):
        return None

    monkeypatch.setattr(Runner, "get_least_busy_backend", get_none)                 
    monkeypatch.setattr(Runner, "execute_task", get_dummy_run_result)
    monkeypatch.setattr(Runner, "handle_statevector", get_none)
    

    