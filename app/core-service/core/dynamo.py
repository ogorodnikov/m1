import io
import os
import json

from boto3 import resource

from decimal import Decimal
from logging import getLogger


class Dynamo:
    
    SERVICE_TASK_RECORD_ID = 0
    GET_QUEUED_TASK_ATTEMPTS = 5

    def __init__(self):
        
        self.logger = getLogger(__name__)
        
        core_bucket_name = os.getenv('CORE_BUCKET')        
        tasks_table_name = os.getenv('TASKS_TABLE_NAME')
        algorithms_table_name = os.getenv('ALGORITHMS_TABLE_NAME')

        db_resource = resource('dynamodb')
        s3_resource = resource('s3')

        self.tasks = db_resource.Table(tasks_table_name)        
        self.algorithms = db_resource.Table(algorithms_table_name)
        self.core_bucket = s3_resource.Bucket(core_bucket_name)
        
        self.tasks.update_item(
            Key={'task_id': self.SERVICE_TASK_RECORD_ID},
            UpdateExpression="SET queued_tasks = if_not_exists(queued_tasks, :empty_list), "
                             "status_updates = if_not_exists(status_updates, :empty_list), "
                             "task_count = if_not_exists(task_count, :zero)",
            ExpressionAttributeValues={':empty_list': [], ':zero': 0}
            )
        
        self.log(f'DYNAMO initiated: {self}')

    
    def log(self, message):
        self.logger.info(message)
        
        
    ###   Algorithms   ###
    
    def get_all_algorithms(self):
    
        scan_response = self.algorithms.scan()
    
        return scan_response.get('Items', {})
    

    def query_algorithms(self, query_parameters):
    
        key_conditions = {}
        
        for filter_name, filter_value in query_parameters.items():
            
            # deprecation warning
            
            key_conditions[filter_name] = {'AttributeValueList': [filter_value],
                                           'ComparisonOperator': "EQ"}
        
        query_response = self.algorithms.query(IndexName='type-index',
                                               KeyConditions=key_conditions)
        
        algorithms = query_response.get('Items', {})
        
        return algorithms
    
    
    def get_algorithm(self, algorithm_id):
    
        item_response = self.algorithms.get_item(Key={'id': algorithm_id})
        
        algorithm = item_response.get('Item', {})
        
        return algorithm
    
    
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
    
        
    ###   Tasks   ###
    
    def get_all_tasks(self):
        
        all_tasks_response = self.tasks.query(
            IndexName='record-type-index',
            KeyConditionExpression="record_type = :record_type",
            ExpressionAttributeValues={":record_type": 'task_record'}
        )

        all_tasks = all_tasks_response.get('Items', [])
        
        all_tasks_replaced = self.replace_decimals(all_tasks)
        
        tasks_dict = {task['task_id']: task for task in all_tasks_replaced}
            
        # self.log(f"DYNAMO tasks_dict keys: {tasks_dict.keys()}")
        
        return tasks_dict
        

    def add_task(self, algorithm_id, run_values):
        
        increment_task_count_response = self.tasks.update_item(

            Key={'task_id': self.SERVICE_TASK_RECORD_ID},
            UpdateExpression="SET task_count = if_not_exists(task_count, :zero) + :n",
            ExpressionAttributeValues={':n': 1, ':zero': 0},
            ReturnValues='ALL_NEW'
            
            )
            
        new_task_id = increment_task_count_response['Attributes'].get('task_count')

        add_queued_task_response = self.tasks.update_item(

            Key={'task_id': self.SERVICE_TASK_RECORD_ID},
            UpdateExpression="SET queued_tasks = " +
                             "list_append(if_not_exists(queued_tasks, :empty_list), :queued_task_id)",
            ExpressionAttributeValues={':empty_list': [],
                                       ':queued_task_id': [new_task_id]},
            ReturnValues='ALL_NEW'
            
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
                                       
            ReturnValues='ALL_NEW'
            )
        
        # self.log(f"DYNAMO add_task {(new_task_id, algorithm_id, run_values)}")

        return new_task_id
        
        
    def get_next_task(self):
        
        queued_task_response = self.tasks.update_item(
                Key={'task_id': self.SERVICE_TASK_RECORD_ID},
                UpdateExpression="REMOVE queued_tasks[0]",
                # ConditionExpression=f"attribute_exists(queued_tasks)",
                ReturnValues='ALL_OLD'
            )
                
        service_task_record = queued_task_response.get('Attributes')
        
        if not service_task_record:
            return None
        
        queued_tasks = service_task_record.get('queued_tasks')
        
        if not queued_tasks:
            return None
            
        next_task_id = queued_tasks[0]

        set_running_status_response = self.tasks.update_item(
            
            Key={'task_id': next_task_id},
            UpdateExpression=f"SET task_status = :new_task_status",
            ExpressionAttributeValues={
                ":new_task_status": 'Running'
            },
            ReturnValues='ALL_NEW'
            
            )

        next_task = set_running_status_response.get('Attributes')
        
        self.log(f"DYNAMO queued_tasks {queued_tasks}")
        self.log(f"DYNAMO next_task_id {next_task_id}")
        # self.log(f"DYNAMO next_task {next_task}")
        
        return next_task


    def update_task_attribute(self, task_id, attribute, value, append=False):

        cleaned_value = json.loads(json.dumps(value), parse_float=Decimal)
        
        if append:
            update_expression = (f"SET {attribute} = "
                                 f"list_append(if_not_exists({attribute}, "
                                 f":empty_list), :{attribute})")
            expression_attribute_values = {f':{attribute}': [cleaned_value],
                                           ':empty_list': []}

        else:
            update_expression = f"SET {attribute} = :{attribute}"
            expression_attribute_values = {f':{attribute}': cleaned_value}            
            
        update_parameters = {
            'Key': {'task_id': task_id},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_attribute_values,
            'ReturnValues': 'ALL_NEW',
            'ReturnItemCollectionMetrics': 'SIZE',
            'ReturnConsumedCapacity': 'INDEXES'
        }
        
        # self.log(f"DYNAMO update_parameters {update_parameters}")
        
        self.tasks.update_item(**update_parameters)
       

    def purge_tasks(self):
        
        self.log(f"DYNAMO purge_tasks")  

        scan_response = self.tasks.scan(ProjectionExpression='task_id')
        scan_response_items = scan_response.get('Items', [])

        while scan_response.get('LastEvaluatedKey'):
            
            scan_response = self.tasks.scan(ExclusiveStartKey=scan_response['LastEvaluatedKey'])
            new_items = scan_response.get('Items', [])
            scan_response_items.extend(new_items)

        with self.tasks.batch_writer() as batch:
            for item in scan_response_items:
                batch.delete_item(Key=item)
                
                
    ###   Statuses   ###
    
    def add_status_update(self, task_id, status, result):
        
        status_update = [int(task_id), status, result]
        
        self.update_task_attribute(task_id, 'task_status', status)
        self.update_task_attribute(task_id, 'task_result', result)
        
        self.update_task_attribute(self.SERVICE_TASK_RECORD_ID, 'status_updates', 
                                   status_update, append=True)
                                   
        # self.log(f'DYNAMO add_status_update {status_update}')
        

    def get_status_updates(self):
        
        status_updates_response = self.tasks.update_item(
            Key={'task_id': self.SERVICE_TASK_RECORD_ID},
            UpdateExpression="SET status_updates = :empty_list",
            ExpressionAttributeValues={':empty_list': []},
            ReturnValues='ALL_OLD'
            )
            
        status_updates_attributes = status_updates_response.get('Attributes')
            
        if not status_updates_attributes:
            return []
        
        status_updates = status_updates_attributes['status_updates']

        replaced_status_updates = self.replace_decimals(status_updates)
                
        # self.log(f"DYNAMO status_updates {status_updates}")
        
        # self.log(f"DYNAMO replaced_status_updates {replaced_status_updates}")
        
        return replaced_status_updates
        
    
    def replace_decimals(self, node):
        
        if isinstance(node, list):
            
            # for i in range(len(node)):
                
            #     node[i] = self.replace_decimals(node[i])
                
            # return node
            
            return list(map(self.replace_decimals, node))
            
        elif isinstance(node, dict):
            
            # for k in node:
                
            #     node[k] = self.replace_decimals(node[k])
                
            # return node
            
            # return {key: self.replace_decimals(value) for key, value in node.items()}
            
            keys, values = zip(*node.items())
            
            replaced_values = map(self.replace_decimals, values)
            
            return dict(zip(keys, replaced_values))
            
        elif isinstance(node, Decimal):
            
            if node % 1:
                return float(node)
            else:
                return int(node)
                
        else:
            return node


    ###   Surprisingly - S3  ###
    
    def move_figure_to_s3(self, from_path, to_path):
        
        self.core_bucket.upload_file(
            from_path, 
            to_path, 
            ExtraArgs={"ACL": "private", "ContentType": "image/png"}
        )
        
        os.remove(from_path)
        
        
    def stream_figure_from_s3(self, s3_from_path) -> io.BytesIO:
        
        figure_stream = io.BytesIO()
        
        self.core_bucket.download_fileobj(s3_from_path, figure_stream)
        
        figure_stream.seek(0)

        return figure_stream
        
        
    def purge_s3_folder(self, prefix):
        
        self.core_bucket.objects.filter(Prefix=prefix).delete()
        
        
    ###   Test Data   ##
    
    def add_test_data(self):
    
        items = [{'id': 'bernvaz',
                  'name': 'Bernstein Vazirani',
                  'type': 'quantum',
                  'description': 'Determines hidden message encoded in black-box function.\n' +
                                 'Classical algorith complexity is O(N) while quantum is O(1).',
                  'wiki_link': 'https://en.wikipedia.org/wiki/Bernstein%E2%80%93Vazirani_algorithm',
                  'qiskit_link': 'https://qiskit.org/textbook/ch-algorithms/bernstein-vazirani.html',
                  'image': b'1010',
                  'parameters': [{'name': 'secret', 'default_value': '1010'}],
                  'color': 'green',
                  'likes': 1324,
                  'enabled': True},
                  
                 {'id': 'egcd',
                  'name': 'Extended Euclidean',
                  'type': 'classical',
                  'description': 'Calculates GCD (Greatest common divisor) and Bézout coefficents.',
                  'wiki_link': 'https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm',
                  'image': b'1010',
                  'parameters': [{'name': 'a', 'default_value': '345'}, 
                                 {'name': 'b', 'default_value': '455244237'}],
                  'color': 'red',
                  'likes': 768,
                  'enabled': True},
                  
                 {'id': 'grover',
                  'name': 'Grover',
                  'type': 'quantum',
                  'description': 'Finds elements which satisfy constraints determined by black-box function.\n' +
                                 'Classical algorith complexity is O(N) while quantum is O(square root of N).',
                  'wiki_link': 'https://en.wikipedia.org/wiki/Grover%27s_algorithm',
                  'qiskit_link': 'https://qiskit.org/textbook/ch-algorithms/grover.html',
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
                  'wiki_link': 'https://en.wikipedia.org/wiki/Grover%27s_algorithm',
                  'qiskit_link': 'https://qiskit.org/textbook/ch-algorithms/grover.html',
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
                  'color': 'yellow',                  
                  'likes': 315,
                  'enabled': True},
                  
                 {'id': 'dj',
                  'name': 'Deutsch Josza',
                  'type': 'quantum',
                  'description': 'Determines if black-box function is constant (returns all 1 or all 0) or balanced ' +
                                 '(returns half of 1 and half of 0).\n' +
                                 'Classical algorith complexity is O(2^N) while quantum is O(1).',
                  'wiki_link': 'https://en.wikipedia.org/wiki/Deutsch%E2%80%93Jozsa_algorithm',
                  'qiskit_link': 'https://qiskit.org/textbook/ch-algorithms/deutsch-jozsa.html',
                  'image': b'1010',
                  'image_url_1': 'https://www.ae-info.org/attach/User/Jozsa_Richard/Jozsa_Richard_small.jpg',
                  'image_url_2': 'https://media.springernature.com/m685/springer-static/image/' +
                                 'art%3A10.1038%2F526S16a/MediaObjects/41586_2015_Article_BF526S16a_Figa_HTML.jpg',
                  'parameters': [{'name': 'secret', 'default_value': '1010'}],
                  'likes': 459,
                  'enabled': True},
    
                 {'id': 'simon',
                  'name': 'Simon',
                  'type': 'quantum',
                  'description': 'Finds period of black-box function.\n' +
                                 'Classical algorithm complexity is O(2^N) while quantum is O(N^3).',
                  'wiki_link': 'https://en.wikipedia.org/wiki/Simon%27s_problem',
                  'qiskit_link': 'https://qiskit.org/textbook/ch-algorithms/simon.html',
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
                  'wiki_link': 'https://en.wikipedia.org/wiki/Quantum_Fourier_transform',
                  'qiskit_link': 'https://qiskit.org/textbook/ch-algorithms/quantum-fourier-transform.html',
                  'image': b'1010',
                  'parameters': [{'name': 'number', 'default_value': '101'}],
                  'likes': 432,
                  'enabled': True},
    
                 {'id': 'qpe',
                  'name': 'Quantum Phase Estimation',
                  'type': 'quantum',
                  'description': 'Estimates phase for unitary operator.',
                  'wiki_link': 'https://en.wikipedia.org/wiki/Quantum_phase_estimation_algorithm',
                  'qiskit_link': 'https://qiskit.org/textbook/ch-algorithms/quantum-phase-estimation.html',
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
                  'wiki_link': 'https://en.wikipedia.org/wiki/Shor%27s_algorithm',
                  'qiskit_link': 'https://qiskit.org/textbook/ch-algorithms/shor.html',
                  'image': b'1010',
                  'parameters': [{'name': 'number', 'default_value': '15'},
                                 {'name': 'base', 'default_value': '2'},
                                 {'name': 'skip_statevector', 'default_value': 'True'}],
                  'color': 'orange',
                  'likes': 2045,
                  'enabled': True},

                 {'id': 'teleport',
                  'name': 'Quantum Teleportation',
                  'type': 'quantum',
                  'description': 'Transfers quantum state using 2 entangled qubits and 2 classical bits.',
                  'wiki_link': 'https://en.wikipedia.org/wiki/Quantum_teleportation',
                  'qiskit_link': 'https://qiskit.org/textbook/ch-algorithms/teleportation.html',
                  'image': b'1010',
                  'parameters': [{'name': 'alpha', 'default_value': 'random'},
                                 {'name': 'beta', 'default_value': 'random'}],
                  'likes': 824,
                  'enabled': True},

                 {'id': 'counting',
                  'name': 'Quantum Counting',
                  'type': 'quantum',
                  'description': 'Uses Grover`s algorithm and QPE to count the number of solutions for given search problem.',
                  'wiki_link': 'https://en.wikipedia.org/wiki/Quantum_counting_algorithm',
                  'qiskit_link': 'https://learn.qiskit.org/course/ch-algorithms/quantum-counting',
                  'image': b'1010',
                  'parameters': [{'name': 'precision', 'default_value': '4'},
                                 {'name': 'secret_1', 'default_value': '1011'},
                                 {'name': 'secret_2', 'default_value': '1010'}],
                  'likes': 974,
                  'enabled': True},

                 {'id': 'bb84',
                  'name': 'BB84 Quantum Key Distribution',
                  'type': 'quantum',
                  'description': 'Securely communicates a private key from one party to another.\n' +
                                 'Uses quantum channel and authenticated public classical channel.',
                  'wiki_link': 'https://en.wikipedia.org/wiki/BB84',
                  'qiskit_link': 'https://qiskit.org/textbook/ch-algorithms/quantum-key-distribution.html',
                  'image': b'1010',
                  'parameters': [{'name': 'alice_bits', 'default_value': '10101'},
                                 {'name': 'alice_bases', 'default_value': 'XXXZX'},
                                 {'name': 'eve_bases', 'default_value': 'XZZZX'},
                                 {'name': 'bob_bases', 'default_value': 'XXXZZ'},
                                 {'name': 'sample_indices', 'default_value': '0, 2'}],
                  'likes': 1028,
                  'enabled': True},

                 {'id': 'qae',
                  'name': 'Quantum Amplitude Estimation',
                  'type': 'quantum',
                  'description': 'Estimates amplitude of quantum state.',
                  'wiki_link': 'https://qiskit.org/documentation/finance/tutorials/00_amplitude_estimation.html#Quantum-Amplitude-Estimation',
                  'qiskit_link': 'https://qiskit.org/documentation/finance/tutorials/00_amplitude_estimation.html#Quantum-Amplitude-Estimation',
                  'image': b'1010',
                  'parameters': [{'name': 'bernoulli_probability', 'default_value': '0.2'},
                                 {'name': 'precision', 'default_value': '3'}],
                  'likes': 246,
                  'enabled': True},

                 {'id': 'iqae',
                  'name': 'Iterative Quantum Amplitude Estimation',
                  'type': 'quantum',
                  'description': 'Estimates amplitude of quantum state using carefully calculated powers of Grover iterations.\n' +
                                 'Does not use Quantum Phase Estimation and Inverse Quantum Fourier Transform parts.\n' +
                                 'Produces much more compact Quantum Circuit compared to Canonical QAE.',
                  'wiki_link': 'https://qiskit.org/documentation/finance/tutorials/00_amplitude_estimation.html#Quantum-Amplitude-Estimation',
                  'qiskit_link': 'https://qiskit.org/documentation/finance/tutorials/00_amplitude_estimation.html#Quantum-Amplitude-Estimation',
                  'image': b'1010',
                  'parameters': [{'name': 'bernoulli_probability', 'default_value': '0.3'},
                                 {'name': 'epsilon', 'default_value': '0.01'},
                                 {'name': 'alpha', 'default_value': '0.05'},
                                 {'name': 'confidence_interval_method', 'default_value': 'clopper_pearson'}],
                  'likes': 816,
                  'enabled': True},
                  
                 ]
        
        with self.algorithms.batch_writer(overwrite_by_pkeys=['id']) as batch:
            for item in items:
                batch.put_item(item)
