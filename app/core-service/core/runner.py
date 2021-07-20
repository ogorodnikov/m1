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
    
    print("Task worker started")
    
    while True:
    
        if worker_active_flag.is_set() and not task_queue.empty():
            
            task_queue.get()
            print("Fetched task!")
            print("Q size:", task_queue.qsize())
    
    print("Task worker exited")
    

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
    
    task = (priority, task_id, runner, run_values)

    
    task_queue.put(task)
    
    app.logger.info(f'RUNNER task: {task}')
    app.logger.info(f'RUNNER task_queue.qsize: {task_queue.qsize()}')
    
    run_result = runner(run_values)

    return run_result