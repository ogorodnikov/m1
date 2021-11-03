import os
import time
import pytest

from threading import Timer

from _pytest.monkeypatch import MonkeyPatch

from qiskit import QuantumCircuit

# from qiskit.providers.ibmq import least_busy

from core.runner import Runner
from core.dynamo import Dynamo


# @pytest.mark.slow
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
    
    def raise_exception(*args, **kwargs):
        raise UserWarning
        
    decorated_raise_exception = Runner.exception_decorator(raise_exception)
    
    decorated_raise_exception(runner, task_id='test_task_id')
        

# @pytest.mark.slow
def test_queue_worker_loop(runner, undecorate):
    
    runner.worker_active_flag.set()
    
    def clear_worker_active_flag():
        runner.worker_active_flag.clear()
    
    test_timer = Timer(interval=1, function=clear_worker_active_flag)
    test_timer.start()
    
    runner.queue_worker_loop()
    
    
def test_get_next_task(runner, undecorate):
    runner.get_next_task()
    

def test_process_next_task(runner, test_task, undecorate):
    runner.process_next_task(test_task)


def test_process_next_task_timeout(runner, test_task, undecorate):
    
    with pytest.raises(TimeoutError, match=r"Task timeout: 0 seconds"):
        runner.process_next_task(test_task, task_timeout=0)
        
        
@pytest.mark.parametrize("mock_runner_functions", 
                         ['post_processing', 'no_post_processing'], 
                         indirect=True)
@pytest.mark.parametrize("run_mode", 
                         ['classical', 'simulator', 'quantum_device'])
def test_run_task_classical(runner, test_task, run_mode, mock_runner_functions, 
                            mock_ibmq_backend, undecorate):
                                
    test_task['run_values']['run_mode'] = run_mode
    
    runner.run_task(**test_task)
    

def test_execute_task(runner, mock_monitor_job):
    
    test_circuit = QuantumCircuit()
    test_backend = runner.simulator_backend
    
    runner.execute_task(task_id=None, circuit=test_circuit, backend=test_backend)
    
    
def test_monitor_job(runner, test_job):
    runner.monitor_job(job=test_job, task_id=None, interval=0)

    
def test_handle_statevector(runner, test_run_result, mock_plot_statevector_figure):
    runner.handle_statevector(run_result=test_run_result, qubit_count=0, task_id=None)


@pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
@pytest.mark.filterwarnings("ignore::::69")
def test_plot_statevector_figure(runner, test_run_result):

    test_statevector = test_run_result.get_statevector(decimals=0)
    
    runner.plot_statevector_figure(statevector=test_statevector, task_id=None)
    

def test_get_least_busy_backend_ok(runner, test_provider, mock_least_busy):
    test_provider.backends_list = 'test_backends'
    runner.get_least_busy_backend(test_provider, qubit_count=0)
    

def test_get_least_busy_backend_exception(runner, test_provider, mock_least_busy):
    with pytest.raises(ValueError):
        runner.get_least_busy_backend(test_provider, qubit_count=0)



###   Fixtures   ###

@pytest.fixture(scope="module")
def runner():

    db = Dynamo()    
    runner = Runner(db)
    
    yield runner

@pytest.fixture(scope="module")
def monkeypatch_module():
    
    monkeypatch_module = MonkeyPatch()
    yield monkeypatch_module
    monkeypatch_module.undo()
    

@pytest.fixture(scope="module")
def test_task():
    
    test_task = {'task_id': '1', 
                 'run_values': {
                     'run_mode': 'test_mode', 
                     'test_parameter_a': 'value_a', 
                     'test_parameter_b': 'value_b',
                 },
                 'algorithm_id': 'test_algorithm'}
                 
    return test_task


@pytest.fixture(scope="module")
def get_test_task(test_task):
    
    def get_test_task_wrapper(*args, **kwargs):
        return test_task
    
    yield get_test_task_wrapper
    

@pytest.fixture(autouse=True, scope="module")
def mocks(monkeypatch_module, get_test_task, stub):
    
    monkeypatch_module.setattr(Dynamo, "add_task", stub)
    monkeypatch_module.setattr(Dynamo, "add_status_update", stub)
    monkeypatch_module.setattr(Dynamo, "update_task_attribute", stub)
    monkeypatch_module.setattr(Dynamo, "move_figure_to_s3", stub)
    
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
def mock_runner_functions(runner, monkeypatch, request, stub):

    def get_dummy_circuit(*args, **kwargs):
        
        class DummyCircuit:
            
            num_qubits = None
            
            def save_statevector(self):
                pass
                
        return DummyCircuit()
    
    monkeypatch.setitem(runner.runner_functions, "test_algorithm", get_dummy_circuit)
    
    if request.param == 'post_processing':
        
        monkeypatch.setitem(runner.post_processing, "test_algorithm", stub)


@pytest.fixture
def test_run_result():
    
    class TestRunResult:
        def get_counts(self):
            return {'test_state': 0}
            
        def get_statevector(self, decimals):
            return [0, 0, 1, 0]
                
    return TestRunResult()
    

@pytest.fixture
def mock_ibmq_backend(monkeypatch, test_run_result, stub):
    
    def get_test_run_result(*args, **kwargs):
        return test_run_result

    monkeypatch.setattr(Runner, "get_least_busy_backend", stub)                 
    monkeypatch.setattr(Runner, "execute_task", get_test_run_result)
    monkeypatch.setattr(Runner, "handle_statevector", stub)
    

@pytest.fixture
def mock_monitor_job(monkeypatch, stub):
    monkeypatch.setattr(Runner, "monitor_job", stub)
    
    
@pytest.fixture
def test_job():

    class Status:
        
        def __init__(self, name):
            self.name = name
        
    class TestJob:
        
        status_queue = [Status('DONE'), Status('QUEUED')]
        
        def status(self):
            return __class__.status_queue.pop()
            
        def queue_position(self):
            pass
            
    return TestJob()
    

@pytest.fixture
def mock_plot_statevector_figure(monkeypatch, stub):
    monkeypatch.setattr(Runner, "plot_statevector_figure", stub)
    

@pytest.fixture
def test_provider():

    class TestProvider:
        
        def __init__(self):
            self.backends_list = None
        
        def backends(self, filters):
            return self.backends_list

    return TestProvider()
    

@pytest.fixture
def mock_least_busy(monkeypatch, stub):
    monkeypatch.setattr("core.runner.least_busy", stub)