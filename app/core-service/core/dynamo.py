import boto3


class DynamoDB():

    def __init__(self, algorithms_table_name, tasks_table_name):

        self.dynamodb = boto3.resource('dynamodb')
        
        self.algorithms = self.dynamodb.Table(algorithms_table_name)
        self.tasks = self.dynamodb.Table(tasks_table_name)
        
        print('DYNAMO connected')
        
    
    def get_all_algorithms(self):
    
        scan_response = self.algorithms.scan()
    
        return scan_response['Items']
    

    def query_algorithms(self, query_parameters):
    
        key_conditions = {}
        
        for filter, value in query_parameters.items():
            
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