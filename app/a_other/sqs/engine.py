def get_task_results_from_sqs(self):
    
    while True:
    
        task_result = self.sqs_result_queue.receive_message()
        
        # app.logger.info(f'RUNNER task_result: {task_result}')
        
        if task_result == None:
            break
            
        task_id, result, status = task_result

        if task_id in self.tasks:

            self.tasks[task_id]['result'] = result            
            self.tasks[task_id]['status'] = status
        
        if status == 'Running':
            continue
        
        yield task_result