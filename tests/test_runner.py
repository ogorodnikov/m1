import os
import time
import pytest

from threading import Timer

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from core.runner import Runner
from core.dynamo import Dynamo


def test_start_stop(runner, monkeypatch, stub):

    monkeypatch.setattr('core.runner.QiskitRuntimeService.save_account', stub)
    monkeypatch.setattr('core.runner.QiskitRuntimeService.delete_account', stub)

    monkeypatch.setattr('core.runner.Runner.queue_worker_loop', stub)
    
    runner.start()
    assert os.environ.get('RUNNER_STATE') == 'Running'
    
    runner.stop()
    assert os.environ.get('RUNNER_STATE') == 'Stopped'


def test_run_algorithm(runner, monkeypatch, stub):
    runner.run_algorithm(None, None)
    

def test_exception_decorator(runner):
    
    def raise_exception(*args, **kwargs):
        raise UserWarning
        
    decorated_raise_exception = Runner.exception_decorator(raise_exception)
    
    decorated_raise_exception(runner, task_id='test_task_id')
        

def test_queue_worker_loop(runner, monkeypatch, stub, undecorate):
    
    monkeypatch.setattr('core.runner.time.sleep', stub)
    
    runner.worker_active_flag.set()
    
    def clear_worker_active_flag():
        runner.worker_active_flag.clear()
    
    test_timer = Timer(interval=0.001, function=clear_worker_active_flag)
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
                         ['classical', 'simulator', 'quantum_device', 'fallback'])
def test_run_task_classical(runner, test_task, run_mode, mock_runner_functions, 
                            mock_ibmq_backend, undecorate):

    if run_mode == 'fallback':

        runner.ibmq_service = None
        run_mode = 'quantum_device'
                 
    test_task['run_values']['run_mode'] = run_mode
    
    runner.run_task(**test_task)


def test_execute_task(runner, test_circuit, monkeypatch, stub):

    test_backend = AerSimulator()

    runner.execute_task(task_id=None, circuit=test_circuit, backend=test_backend)


def test_monitor_job(runner, test_job, monkeypatch):

    runner.monitor_job(job=test_job, task_id=None, interval=0)

    
def test_handle_statevector(runner, test_circuit, monkeypatch, stub):
    
    monkeypatch.setattr(Runner, "plot_statevector_figure", stub)

    runner.handle_statevector(circuit=test_circuit, task_id=None)


@pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
@pytest.mark.filterwarnings("ignore::::69")
def test_plot_statevector_figure(runner, monkeypatch, stub, test_run_result):
    
    class MockFigure:
        savefig = stub
    
    monkeypatch.setattr('core.runner.plot_bloch_multivector', 
                        lambda statevector: MockFigure())
                        
    test_statevector = test_run_result.get_statevector(decimals=0)
    
    runner.plot_statevector_figure(statevector=test_statevector, task_id=None)
    

def test_get_least_busy_backend_ok(runner):

    runner.get_least_busy_backend(runner.ibmq_service, qubit_count=0, 
                                  backend_avoid_list=[])


###   Fixtures   ###

@pytest.fixture(scope="module", autouse=True)
def set_mocks(mock, mock_env, get_test_task, stub):
    
    mock(Dynamo, "__init__", stub)
    mock(Dynamo, "add_task", stub)
    mock(Dynamo, "add_status_update", stub)
    mock(Dynamo, "update_task_attribute", stub)
    mock(Dynamo, "move_figure_to_s3", stub)
    
    mock(Dynamo, "get_next_task", get_test_task)

    mock_env('QISKIT_TOKEN', '1234')    
    mock_env('TASK_TIMEOUT', '300')
    mock_env('BACKEND_AVOID_STRING', '')
    mock_env('QUEUE_WORKERS_PER_RUNNER', '1')


@pytest.fixture
def runner(stub):

    runner = Runner(db=Dynamo())

    class MockIBMQService:
        least_busy = stub
        backends = lambda *_, **__: ['backend_1', 'backend_2']

    runner.ibmq_service = MockIBMQService()

    return runner


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
    
    return get_test_task_wrapper


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
        
    class TestCircuit:
        num_qubits = None
        save_statevector = stub
    
    monkeypatch.setitem(runner.runner_functions, "test_algorithm",
                        lambda *_, **__: TestCircuit())
    
    if request.param == 'post_processing':
        
        monkeypatch.setitem(runner.post_processing, "test_algorithm", stub)
        

@pytest.fixture
def mock_ibmq_backend(monkeypatch, test_run_result, stub):

    monkeypatch.setattr(Runner, "get_least_busy_backend", stub)                 
    monkeypatch.setattr(Runner, "execute_task", lambda *_, **__: test_run_result)
    monkeypatch.setattr(Runner, "handle_statevector", stub)


@pytest.fixture
def test_circuit():

    test_circuit = QuantumCircuit(2, 2)

    test_circuit.x(0)
    test_circuit.cx(0, 1)

    test_circuit.measure([0, 1], [0, 1])

    return test_circuit


@pytest.fixture
def test_run_result():
    
    class TestRunResult:
        def get_counts(self):
            return {'test_state': 0}
            
        def get_statevector(self, decimals):
            return [0, 0, 1, 0]
                
    return TestRunResult()
    

@pytest.fixture
def test_job(test_run_result):

    class TestJob:

        status_queue = ['DONE', 'DONE', 'QUEUED', 'QUEUED']
        
        def status(self):
            return self.status_queue.pop()

        def job_id(self):
            return 1234     
            
        def metrics(self):
            return {'position_in_queue': 1}

    return TestJob()
