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


# def test_state(runner):
#     assert os.environ.get('RUNNER_STATE') == 'Running'


def test_log(runner):
    runner.log(message='test', task_id=1)
    

def test_run_algorithm(runner):
    runner.run_algorithm(None, None)
    
    
def test_get_next_task(runner):
    runner.get_next_task()
    
 
def test_queue_worker(runner):
    
    # print(runner.queue_worker)
    # print(Runner.queue_worker)
    
    # pytest.fail()
    
    def clear_worker_active_flag():
        runner.worker_active_flag.clear()
    
    test_timer = Timer(interval=1, function=clear_worker_active_flag)
    test_timer.start()
    
    runner.queue_worker.__wrapped__(self=runner)

    # print('runner.queue_worker.__wrapped__', runner.queue_worker.__wrapped__)
    
    
    # def decorator(function):
    #     def wrapper():
    #         return function()
    #     return wrapper
        
    # @decorator
    # def decorated():
    #     pass
    
    # print('>>>', decorated.__closure__[0].cell_contents)
    
    # pytest.fail()
    
    # runner.queue_worker.__closure__[1].cell_contents()
    
    
    # test_thread = Thread(target=runner.queue_worker)
    # test_thread.start()
    
    # time.sleep(3)
    
    # runner.worker_active_flag.clear()
    
    
    # test_process = Process(target=runner.queue_worker)
    
    # test_process.start()
    # test_process.join(3)

    # test_process.terminate()
    # test_process.join()    
    
    # test_pool = ProcessPoolExecutor()
    # test_pool.submit(runner.queue_worker)
    
    # runner.queue_worker()
    
    # runner.worker_active_flag.clear()


###   Fixtures   ###

@pytest.fixture(scope="module")
def runner():

    db = Dynamo()    
    runner = Runner(db
    )
    # runner.start()
    
    yield runner
    
    # runner.stop()
    

@pytest.fixture(scope="module")
def monkeypatch_module(request):
    
    monkeypatch_module = MonkeyPatch()
    yield monkeypatch_module
    monkeypatch_module.undo()
    

@pytest.fixture(autouse=True, scope="module")
def mocks(monkeypatch_module):
    
    def stub(*args, **kwargs):
        pass
    
    def get_next_task(self):
        return 'test_next_task'
        
    monkeypatch_module.setattr(Dynamo, "add_task", stub)
    monkeypatch_module.setattr(Dynamo, "add_status_update", stub)
    monkeypatch_module.setattr(Dynamo, "update_task_attribute", stub)
    
    monkeypatch_module.setattr(Dynamo, "get_next_task", get_next_task)
    

