from multiprocessing import Process, Event, Queue, Manager, Pool

from concurrent.futures import ProcessPoolExecutor

import os, time


class Test():
    
    def __init__(self):
        

        
        self.manager = Manager()
        self.results = self.manager.list()
        
        
        # self.start_pool()
        
        self.start_pool_executor()
        
        
    def start_pool(self):
        
        pool = Pool(processes=1)
        
        print(f'RUNNER pool: {pool}') 
        
        pool_result = pool.apply_async(self.task_worker, ("ok",))
    
        pool_result_data = pool_result.get(timeout=5)
            
        print(f'RUNNER pool_result: {pool_result}')
        print(f'RUNNER pool_result_data: {pool_result_data}')
        

        
    def start_pool_executor(self):
        
        pool_executor = ProcessPoolExecutor(max_workers=3, 
                                            initializer=self.task_worker,
                                            initargs=("test message",))

        print(f'RUNNER pool_executor: {pool_executor}')
        
        pool_executor.submit(self.task_worker)
        
        

    def task_worker(self, message):
        
        print(f'RUNNER task_worker started: {os.getpid()} - {message}')
        
        task_worker_process = Process(target=self.run_function,
                                       args=(self.results,),
                                       name=f"Process-task-worker",
                                       daemon=False)
                       
        task_worker_process.start()
        
        time.sleep(1)
        
        print(f'RUNNER task_worker results: {self.results}')
        
        
    def run_function(self, results):
        
        results.append(os.getpid())
        
        print(f'RUNNER run_function results: {self.results}')
        

        

test = Test()