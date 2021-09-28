import boto3


class DB():
    
    SERVICE_TASK_RECORD_ID = 0
    GET_QUEUED_TASK_ATTEMPTS = 5

    def __init__(self, app):
        
        tasks_table_name = app.config.get('TASKS_TABLE_NAME')
        algorithms_table_name = app.config.get('ALGORITHMS_TABLE_NAME')

        self.db_resource = boto3.resource('dynamodb')

        self.tasks = self.db_resource.Table(tasks_table_name)        
        self.algorithms = self.db_resource.Table(algorithms_table_name)
        
        app.config['DB'] = self
        app.logger.info('DYNAMO initiated')
        
    
    # Algorithms
    
    def get_all_algorithms(self):
    
        scan_response = self.algorithms.scan()
    
        return scan_response.get('Items', {})
    

    def query_algorithms(self, query_parameters):
    
        key_conditions = {}
        
        for filter, value in query_parameters.items():
            
            # deprecation warning
            
            key_conditions[filter] = {'AttributeValueList': [value], 
                                      'ComparisonOperator': "EQ"}
        
        query_response = self.algorithms.query(IndexName='type-index',
                                               KeyConditions=key_conditions)
        
        return query_response['Items']
    
    
    def get_algorithm(self, algorithm_id):
    
        item_response = self.algorithms.get_item(Key={'id': algorithm_id})
        
        return item_response['Item']
    
    
    def like_algorithm(self, algorithm_id):
    
        update_response = self.algorithms.update_item(
            
            Key={'id': algorithm_id},
            UpdateExpression="SET likes = likes + :n",
            ExpressionAttributeValues={':n': 1})
            
        status_code = update_response['ResponseMetadata']['HTTPStatusCode']
            
        return {'status_code': status_code}
        
    
    def set_algorithm_state(self, algorithm_id, is_enabled):
        
        update_response = self.algorithms.update_item(
            
            Key={'id': algorithm_id},
            UpdateExpression="SET enabled = :b",
            ConditionExpression=f"attribute_exists(id)",
            ExpressionAttributeValues={':b': is_enabled})
    
        status_code = update_response['ResponseMetadata']['HTTPStatusCode']
            
        return {'status_code': status_code}
    
    
    
        
    ### Tasks
    
    def get_all_tasks(self):
        
        all_tasks_response = self.tasks.query(
            IndexName='record-type-index',
            KeyConditionExpression="record_type = :record_type",
            ExpressionAttributeValues={":record_type": 'task_record'}
        )

        # print(f"DYNAMO all_tasks_response {all_tasks_response}")    

        all_tasks = all_tasks_response.get('Items', [])
        
        tasks_dict = {}
        
        for task in all_tasks:
            
            task_id = int(task['task_id'])
            
            tasks_dict[task_id] = task
            
        # print(f"DYNAMO all_tasks {all_tasks}")
        # print(f"DYNAMO tasks_dict:")
        # for task_id, values in tasks_dict.items():
        #     print(f"DYNAMO {task_id}: {values}\n")       
    
        return tasks_dict
        

    def add_task(self, algorithm_id, run_values):
        
        increment_task_count_response = self.tasks.update_item(

            Key={'task_id': self.SERVICE_TASK_RECORD_ID},
            UpdateExpression="SET task_count = if_not_exists(task_count, :zero) + :n",
            ExpressionAttributeValues={':n': 1, ':zero': 0},
            ReturnValues = 'ALL_NEW'
            
            )

        new_task_id = increment_task_count_response['Attributes']['task_count']

        add_queued_task_response = self.tasks.update_item(

            Key={'task_id': self.SERVICE_TASK_RECORD_ID},
            UpdateExpression="SET queued_tasks = list_append(if_not_exists(queued_tasks, :empty_list), :queued_task_id)",
            ExpressionAttributeValues={':empty_list': [],
                                       ':queued_task_id': [new_task_id]},
            ReturnValues = 'ALL_NEW'
            
            )
        
        new_task_response = self.tasks.update_item(

            Key={'task_id': new_task_id},
            
            UpdateExpression="SET algorithm_id = :algorithm_id, "
                             "run_values = :run_values, "
                             "task_status = :task_status, "
                             "record_type = :record_type, "
                             "logs = :logs",
                             
            ExpressionAttributeValues={':algorithm_id': algorithm_id,
                                       ':run_values': run_values,
                                       ':task_status': 'Queued',
                                       ':record_type': 'task_record',
                                       ':logs': []},
                                       
            ReturnValues = 'ALL_NEW'
            
            )
        
        print(f"DYNAMO add_task {(new_task_id, algorithm_id, run_values)}")

        return new_task_id
        
        
    def get_queued_task(self):
        
        # print(f"DYNAMO get_queued_task")
        
        queued_task_response = self.tasks.update_item(
        
                Key={'task_id': self.SERVICE_TASK_RECORD_ID},
                UpdateExpression="REMOVE queued_tasks[0]",
                # ExpressionAttributeValues={':n': 1, ':zero': 0},
                ReturnValues = 'ALL_OLD'
            
            )
            
        # print(f"DYNAMO queued_task_response {queued_task_response}")
            
        service_task_record = queued_task_response.get('Attributes')
        
        # print(f"DYNAMO service_task_record {service_task_record}")
        
        if not service_task_record:
            return None
        
        queued_tasks = service_task_record.get('queued_tasks')
        
        # print(f"DYNAMO queued_tasks {queued_tasks}")
        
        if not queued_tasks:
            return None
            
        next_task_id = queued_tasks[0]
            
        # print(f"DYNAMO next_task_id {next_task_id}")

        set_running_status_response = self.tasks.update_item(
            
            Key={'task_id': next_task_id},
            UpdateExpression=f"SET task_status = :new_task_status",
            ExpressionAttributeValues={
                ":new_task_status": 'Running'
            },
            ReturnValues = 'ALL_NEW'
            
            )

        # print(f"DYNAMO set_running_status_response {set_running_status_response}")
        
        next_task = set_running_status_response.get('Attributes')

        print(f"DYNAMO next_task {next_task}")
        
        return next_task


    def update_task_attribute(self, task_id, attribute, value, append=False, if_exists=False):

        # print(f"DYNAMO update_task_attribute: {task_id, attribute, value, append, if_exists}")
        
        if append:
            update_expression = f"SET {attribute} = list_append({attribute}, :{attribute})"
        else:
            update_expression = f"SET {attribute} = :{attribute}"
            
        update_parameters = {
            'Key': {'task_id': task_id},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': {f":{attribute}": value},
            'ReturnValues': 'ALL_NEW'
        }
        
        if if_exists:
            update_parameters['ConditionExpression'] = f"attribute_exists({attribute})"
        
        # print(f"DYNAMO update_parameters {update_parameters}")
        
        update_task_response = self.tasks.update_item(**update_parameters)
       
        # print(f"DYNAMO update_task_response {update_task_response}")
        

    def purge_tasks(self):

        scan_response = self.tasks.scan(ProjectionExpression='task_id')
        
        scan_response_items = scan_response['Items']

        while scan_response.get('LastEvaluatedKey'):
            
            scan_response = self.tasks.scan(ExclusiveStartKey=scan_response['LastEvaluatedKey'])
            
            scan_response_items.extend(scan_response['Items'])
        
        print(f"DYNAMO purging all tasks")        

        with self.tasks.batch_writer() as batch:
            for item in scan_response_items:
                batch.delete_item(Key=item)
                
                
    ###   Statuses
    
    def add_status_update(self, task_id, status, result):
        
        print(f'DYNAMO add_status_update {task_id, status, result}')
        
        self.update_task_attribute(task_id, 'task_status', status)
        self.update_task_attribute(task_id, 'task_result', result)
        
        status_update = [task_id, status, result]
        
        add_status_update_response = self.tasks.update_item(
            Key={'task_id': self.SERVICE_TASK_RECORD_ID},
            UpdateExpression="SET status_updates = list_append(if_not_exists(status_updates, :empty_list), :status_update)",
            ExpressionAttributeValues={':empty_list': [],
                                       ':status_update': [status_update]},
            ReturnValues = 'ALL_NEW'
            )


    def get_status_updates(self):
        
        status_updates_response = self.tasks.update_item(
            Key={'task_id': self.SERVICE_TASK_RECORD_ID},
            UpdateExpression="SET status_updates = :empty_list",
            ExpressionAttributeValues={':empty_list': []},
            ReturnValues = 'ALL_OLD'
            )
            
        # print(f"DYNAMO status_updates_response {status_updates_response}")
                
        status_updates_attributes = status_updates_response.get('Attributes')
            
        if not status_updates_attributes:
            return []
        
        status_updates = status_updates_attributes['status_updates']
                
        # print(f"DYNAMO status_updates {status_updates}")
        
        return status_updates



    def add_test_data(self):
    
        items = [{'id': 'bernvaz',
                  'name': 'Bernstein Vazirani',
                  'type': 'quantum',
                  'description': 'Determines hidden message encoded in black-box function.\n' +
                                 'Classical algorith complexity is O(N) while quantum is O(1).',
                  'link': 'https://en.wikipedia.org/wiki/Bernstein%E2%80%93Vazirani_algorithm',
                  'image': b'1010',
                  'parameters': [{'name': 'secret', 'default_value': '1010'}],
                  'likes': 1324,
                  'enabled': True},
                  
                  {'id': 'egcd',
                  'name': 'Extended Euclidean',
                  'type': 'classical',
                  'description': 'Calculates GCD (Greatest common divisor) and Bézout coefficents.',
                  'link': 'https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm',
                  'image': b'1010',
                  'parameters': [{'name': 'a', 'default_value': '345'}, 
                                 {'name': 'b', 'default_value': '455244237'}],
                  'likes': 768,
                  'enabled': True},
                  
                  {'id': 'grover',
                  'name': 'Grover',
                  'type': 'quantum',
                  'description': 'Finds elements which satisfy constraints determined by black-box function.\n' +
                                 'Classical algorith complexity is O(N) while quantum is O(square root of N).',
                  'link': 'https://en.wikipedia.org/wiki/Grover%27s_algorithm',
                  'image': b'1010',
                  'parameters': [{'name': 'secret_1', 'default_value': '10111'}, 
                                 {'name': 'secret_2', 'default_value': '10101'}],
                  'likes': 457,
                  'enabled': True},
                  
                  {'id': 'grover_sudoku',
                  'name': 'Grover Mini Sudoku',
                  'type': 'quantum',
                  'description': 'Finds elements in sudoku-style matrix using Grover quantum search algorithm.\n' +
                                 'Classical algorith complexity is O(N) while quantum is O(square root of N).',
                  'link': 'https://en.wikipedia.org/wiki/Grover%27s_algorithm',
                  'image': b'1010',
                  'parameters': [
                      {'name': 'row_1', 'default_value': '1.'},
                      {'name': 'row_2', 'default_value': '.'},
                      {'name': 'row_3', 'default_value': ''},
                      {'name': 'width', 'default_value': 'autodetect'},
                      {'name': 'height', 'default_value': 'autodetect'},
                      {'name': 'maximum_digit', 'default_value': 'autodetect'},
                      {'name': 'repetitions_limit', 'default_value': '3'},
                      {'name': 'solutions_count', 'default_value': '2'}],
                  'likes': 315,
                  'enabled': True},
                  
                  {'id': 'dj',
                  'name': 'Deutsch Josza',
                  'type': 'quantum',
                  'description': 'Determines if black-box function is constant (returns all 1 or all 0) or balanced (returns half of 1 and half of 0).\n' +
                                 'Classical algorith complexity is O(2^N) while quantum is O(1).',
                  'link': 'https://en.wikipedia.org/wiki/Deutsch%E2%80%93Jozsa_algorithm',
                  'image': b'1010',
                  'image_url_1': 'https://www.ae-info.org/attach/User/Jozsa_Richard/Jozsa_Richard_small.jpg',
                  'image_url_2': 'https://media.springernature.com/m685/springer-static/image/art%3A10.1038%2F526S16a/MediaObjects/41586_2015_Article_BF526S16a_Figa_HTML.jpg',
                  'parameters': [{'name': 'secret', 'default_value': '1010'}],
                  'likes': 459,
                  'enabled': True},
    
                  {'id': 'simon',
                  'name': 'Simon',
                  'type': 'quantum',
                  'description': 'Finds period of black-box function.\n' +
                                 'Classical algorithm complexity is O(2^N) while quantum is O(N^3).',
                  'link': 'https://en.wikipedia.org/wiki/Simon%27s_problem',
                  'image': b'1010',
                  'parameters': [{'name': 'period', 'default_value': '1010'},
                                 {'name': 'masquerade', 'default_value': 'True'}],
                  'likes': 781,
                  'enabled': True},
    
                  {'id': 'qft',
                  'name': 'Quantum Fourier Transform',
                  'type': 'quantum',
                  'description': 'Applies discrete Fourier transform to quantum state amplitudes.\n' +
                                 'Classical algorithm complexity is O(N*2^N) while quantum is O(N*log(N)).',
                  'link': 'https://en.wikipedia.org/wiki/Quantum_Fourier_transform',
                  'image': b'1010',
                  'parameters': [{'name': 'number', 'default_value': '101'}],
                  'likes': 432,
                  'enabled': True},
    
                  {'id': 'qpe',
                  'name': 'Quantum Phase Estimation',
                  'type': 'quantum',
                  'description': 'Estimates phase for unitary operator.',
                  'link': 'https://en.wikipedia.org/wiki/Quantum_phase_estimation_algorithm',
                  'image': b'1010',
                  'parameters': [{'name': 'angle', 'default_value': '0.25'},
                                 {'name': 'precision', 'default_value': '3'}],              
                  'likes': 395,
                  'enabled': True},
    
                  {'id': 'shor',
                  'name': 'Shor',
                  'type': 'quantum',
                  'description': 'Factors integers using quantum spectographer and modular exponentiation.\n' +
                                 'Classical algorithm complexity is O(2 ^ square root of N) while quantum is O(N^3).',
                  'link': 'https://en.wikipedia.org/wiki/Shor%27s_algorithm',
                  'image': b'1010',
                  'parameters': [{'name': 'number', 'default_value': '330023'}],              
                  'likes': 2045,
                  'enabled': True},
                                
                  ]
        
        with self.algorithms.batch_writer(overwrite_by_pkeys=['id']) as batch:
            for item in items:
                batch.put_item(item)