from multiprocessing import Process, Event, Queue, Manager, Pool

import os


def test_func(data):
    
    print(f'RUNNER test_func: {data}')
    
    return "result" + data
    

task_process_count = 1

tasks_pool = Pool(processes=task_process_count)





def run_task(number):

    for i in range(number):
        
        pool_result = tasks_pool.apply_async(test_func, ("ok",))
        
        # pool_result = tasks_pool.apply_async(os.getpid, ())
        
        pool_result_data = pool_result.get(timeout=10)
        
        print(f'RUNNER pool_result: {pool_result}')
        print(f'RUNNER pool_result_data: {pool_result_data}')
        

run_task(1000)