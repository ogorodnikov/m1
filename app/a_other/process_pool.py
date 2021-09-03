from multiprocessing import Process, Event, Queue, Manager, Pool

from concurrent.futures import ProcessPoolExecutor

import os, time


class Test():
    
    def __init__(self):
        
        # queue_workers_pool = Pool(processes=1)
        
        # print(f'RUNNER queue_workers_pool: {queue_workers_pool}') 
        
        
        # pool_result = queue_workers_pool.apply_async(self.task_worker, ("ok",))
    
        # pool_result_data = pool_result.get(timeout=5)
            
        # print(f'RUNNER pool_result: {pool_result}')
        # print(f'RUNNER pool_result_data: {pool_result_data}')
        
        self.manager = Manager()
        self.results = self.manager.list()
        
        self.start_pool_executor()
        

        
    def start_pool_executor(self):
        
        queue_workers_pool = ProcessPoolExecutor(max_workers=3, 
                                                 initializer=self.task_worker,
                                                 initargs=("test message",))

        # print(f'RUNNER queue_workers_pool: {queue_workers_pool}')
        
        queue_workers_pool.submit(self.task_worker)
        
        

    def task_worker(self, message):
        
        print(f'RUNNER task_worker started: {os.getpid()} - {message}')
        
        task_worker_process = Process(target=self.run_function,
                                       args=(self.results,),
                                       name=f"Process-task-worker",
                                       daemon=False)
                       
        task_worker_process.start()
        
        time.sleep(3)
        
        print(f'RUNNER self.results: {self.results}')
        
        
    def run_function(self, results):
        
        print(f'RUNNER self.results: {self.results}')
        results.append(os.getpid())

        

test = Test()

# test.run_task(1)