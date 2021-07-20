from queue import PriorityQueue

import threading
import time

from core import app

from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz


runners = {'egcd': egcd,
           'bernvaz': bernvaz}
           
task_queue = PriorityQueue()
task_id = 0


def test_runner(task_queue, is_runner_active):
    
    print("Before Bonya test")
    
    while is_runner_active.is_set():

        print("Bonya test")
        time.sleep(0.5)
    
    print("After Bonya test")
    

is_runner_active = threading.Event()
is_runner_active.set()

# with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
#     executor.submit(test_runner, task_queue, is_runner_active)
    
    # time.sleep(2.5)
    
    # is_runner_active.clear()
    
runner_thread = threading.Thread(target=test_runner, 
                                 args=(task_queue, is_runner_active),
                                 daemon=True)

runner_thread.start()
    

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