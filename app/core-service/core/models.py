import boto3


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('m1-algorithms-table')


def add_test_data():

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
              'parameters': [{'name': 'a', 'default_value': '345'}, {'name': 'b', 'default_value': '455244237'}],
              'likes': 768,
              'enabled': True},
              
              {'id': 'grover',
              'name': 'Grover',
              'type': 'quantum',
              'description': 'Finds elements which satisfy constraints determined by black-box function.\n' +
                             'Classical algorith complexity is O(N) while quantum is O(square root of N).',
              'link': 'https://en.wikipedia.org/wiki/Grover%27s_algorithm',
              'image': b'1010',
              'parameters': [{'name': 'secret_1', 'default_value': '10111'}, {'name': 'secret_2', 'default_value': '10101'}],
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
                  {'name': 'solutions_count', 'default_value': '2'},
                  ],
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
                             {'name': 'masquerade', 'default_value': 'True'},],
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
              'parameters': [{'name': 'theta', 'default_value': '0.25'},
                             {'name': 'precision', 'default_value': '3'},],              
              'likes': 395,
              'enabled': True},
              
              ]
    
    with table.batch_writer(overwrite_by_pkeys=['id']) as batch:
        for item in items:
            batch.put_item(item)
         
            
def get_all_algorithms():
    
    response = table.scan()

    return response['Items']
    

def query_algorithms(query_parameters):

    key_conditions = {}
    
    for filter, value in query_parameters.items():
        
        key_conditions[filter] = {'AttributeValueList': [value], 
                                  'ComparisonOperator': "EQ"}
    
    response = table.query(IndexName='type-index',
                           KeyConditions=key_conditions)
    
    return response['Items']


def get_algorithm(algorithm_id):

    response = table.get_item(Key={'id': algorithm_id})
    
    return response['Item']


def like_algorithm(algorithm_id):

    response = table.update_item(
        
        Key={'id': algorithm_id},
        UpdateExpression="SET likes = likes + :n",
        ExpressionAttributeValues={':n': 1})
        
    status_code = response['ResponseMetadata']['HTTPStatusCode']
        
    return {'status_code': status_code}
    

def set_algorithm_state(algorithm_id, is_enabled):
    
    response = table.update_item(
        
        Key={'id': algorithm_id},
        UpdateExpression="SET enabled = :b",
        ConditionExpression=f"attribute_exists(id)",
        ExpressionAttributeValues={':b': is_enabled})

    status_code = response['ResponseMetadata']['HTTPStatusCode']
        
    return {'status_code': status_code}
    
    
def check_credentials():
    
    import os
    
    os.environ['AWS_PROFILE'] = "default"
    os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
    
    print("MODELS available_profiles:", boto3.session.Session().available_profiles)
    
    boto3.setup_default_session(profile_name='default')
    
    table.scan()
    
    print("Connected to 'm1-algorithms-table'")