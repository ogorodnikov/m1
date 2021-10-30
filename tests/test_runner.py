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
    runner.process_next_task(get_test_task())


def test_run_task(runner):
    ...
    
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
                     'run_values': 'test_run_values',
                     'algorithm_id': 'test_algorithm_id'}
        
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