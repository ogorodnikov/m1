from queue import PriorityQueue

import threading
import time

from core import app

from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz



from concurrent.futures import ThreadPoolExecutor


MAX_TASK_WORKERS = 1

task_executor = ThreadPoolExecutor(MAX_TASK_WORKERS)


def task_worker(task_queue, worker_active_flag):
    
    app.logger.info(f'RUNNER task_worker started')
    
    while True:
    
        if worker_active_flag.is_set() and not task_queue.empty():
            
            pop_task = task_queue.get()
            
            app.logger.info(f'RUNNER pop_task: {pop_task}')
            app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
    
    app.logger.info(f'RUNNER task_worker exited')
    

runners = {'egcd': egcd,
           'bernvaz': bernvaz}
           
task_queue = PriorityQueue()
task_id = 0


worker_active_flag = threading.Event()
worker_active_flag.set()

# with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
#     executor.submit(test_runner, task_queue, is_runner_active)
    
    # time.sleep(2.5)
    
    # is_runner_active.clear()
    
# runner_thread = threading.Thread(target=test_runner, 
#                                  args=(task_queue, is_runner_active),
#                                  daemon=True)

# runner_thread.start()

task_executor.submit(task_worker, task_queue, worker_active_flag)
    
    

def run_algorithm(algorithm_id, run_values):
    
    priority = 1
    runner = runners[algorithm_id]
    
    global task_id
    task_id += 1
    
    new_task = (priority, task_id, runner, run_values)

    
    task_queue.put(new_task)
    
    app.logger.info(f'RUNNER new_task: {new_task}')
    app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
    
    run_result = runner(run_values)

    return run_result