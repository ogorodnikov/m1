from queue import PriorityQueue

import threading
import time

from core import app

from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz

from flask import flash


from concurrent.futures import ThreadPoolExecutor


MAX_TASK_WORKERS = 2

task_executor = ThreadPoolExecutor(MAX_TASK_WORKERS)


def test_excepthook(args):
    
    print(f"Test excepthook: {args}")
    

# threading.excepthook = test_excepthook


def task_worker(task_queue, result_queue, worker_active_flag):
    
    app.logger.info(f'RUNNER task_worker started')
    
    while True:
    
        if worker_active_flag.is_set() and not task_queue.empty():
            
            pop_task = task_queue.get()
            
            priority, task_id, algorithm_id, run_values = pop_task
            
            runner = runners[algorithm_id]
            
            app.logger.info(f'RUNNER pop_task: {pop_task}')
            app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
            app.logger.info(f'RUNNER runner: {runner}')            
            
            app.logger.info(f'RUNNER test')
            
            show_flash()
            
            run_result = runner(run_values)
            
            # result_queue.put(task_id, run_results)
            
            app.logger.info(f'RUNNER run_result: {run_result}')
            
            app.logger.info(f'RUNNER show_flash: {show_flash}')
            

            

            # app.logger.info(f'RUNNER result_queue.qsize: {result_queue.qsize()}')          

            # test = show_flash()
            
            # app.logger.info(f'RUNNER test: {test}')
            
            # app.logger.info(f'RUNNER flask.current_app: {flask.current_app, flask.has_request_context()}')

            
            # flash(f"Result: {run_result}", category='info')
            
    
    app.logger.info(f'RUNNER task_worker exited')
    

runners = {'egcd': egcd,
           'bernvaz': bernvaz}

task_id = 0          
task_queue = PriorityQueue()
result_queue = PriorityQueue()

worker_active_flag = threading.Event()
worker_active_flag.set()

task_executor.submit(task_worker, task_queue, result_queue, worker_active_flag)
    

def run_algorithm(algorithm_id, run_values):
    
    priority = 1

    global task_id
    task_id += 1
    
    new_task = (priority, task_id, algorithm_id, run_values)
    
    task_queue.put(new_task)
    
    app.logger.info(f'RUNNER new_task: {new_task}')
    app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
    
    # return run_result
    

def show_flash():
    
    flash("Test", category='info')
    
    return 'test'