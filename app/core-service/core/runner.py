from queue import PriorityQueue

import threading
import time

from core import app

from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz

from concurrent.futures import ThreadPoolExecutor


# MAX_TASK_WORKERS = 2

# task_executor = ThreadPoolExecutor(MAX_TASK_WORKERS)



def task_worker(task_queue, result_queue, worker_active_flag):
    
    app.logger.info(f'RUNNER task_worker started')
    
    while True:
        
        time.sleep(1)
    
        if worker_active_flag.is_set() and not task_queue.empty():
            
            pop_task = task_queue.get()
            
            priority, task_id, algorithm_id, run_values = pop_task
            
            runner = runners[algorithm_id]
            
            app.logger.info(f'RUNNER pop_task: {pop_task}')
            app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
            app.logger.info(f'RUNNER runner: {runner}')            

            result = runner(run_values)
            
            app.logger.info(f'RUNNER result: {result}')
            app.logger.info(f'RUNNER result_queue.qsize: {result_queue.qsize()}')
            
            result_queue.put((task_id, result))
            
            tasks[task_id]['status'] = 'Done'
            tasks[task_id]['result'] = result
            
            app.logger.info(f'RUNNER tasks: {tasks}')            


    
    app.logger.info(f'RUNNER task_worker exited')
    

runners = {'egcd': egcd,
           'bernvaz': bernvaz}

task_id = 0          
task_queue = PriorityQueue()
result_queue = PriorityQueue()
tasks = {}

worker_active_flag = threading.Event()
worker_active_flag.set()

task_worker_thread = threading.Thread(target=task_worker,
                                      args=(task_queue, result_queue, worker_active_flag),
                                      daemon=True)
                                      
task_worker_thread.start()

# task_executor.submit(task_worker, task_queue, result_queue, worker_active_flag)
    

def run_algorithm(algorithm_id, run_values):
    
    priority = 1

    global task_id
    task_id += 1
    
    new_task = (priority, task_id, algorithm_id, run_values)
    
    tasks[task_id] = {'algorithm_id': algorithm_id,
                      'run_values': run_values,
                      'status': 'Created'}
                      
    task_queue.put(new_task)
    
    app.logger.info(f'RUNNER new_task: {new_task}')
    app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
    app.logger.info(f'RUNNER task_id: {task_id}')
    
    return task_id
    

