from queue import PriorityQueue

from core import app

from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz


runners = {'egcd': egcd,
           'bernvaz': bernvaz}
           
task_queue = PriorityQueue()
task_id = 0

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