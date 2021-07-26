import boto3, json


###   Credential check   ###

# import os
# os.environ['AWS_PROFILE'] = "default"
# os.environ['AWS_DEFAULT_REGION'] = "us-east-1"

# print("Profiles:", boto3.session.Session().available_profiles)
# boto3.setup_default_session(profile_name='default')

# table.scan()
# print("Connected to 'm1-algorithms-table'")


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
              'parameters': ['secret'],
              'likes': 1324,
              'enabled': True},
              
              {'id': 'egcd',
              'name': 'Extended Euclidean',
              'type': 'classic',
              'description': 'Calculates GCD (Greatest common divisor) and Bézout coefficents.',
              'link': 'https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm',
              'image': b'1010',
              'parameters': ['a', 'b'],
              'likes': 768,
              'enabled': True},
              
              {'id': 'grover',
              'name': 'Grover',
              'type': 'quantum',
              'description': 'Finds elements which satisfy constraints determined by black-box function.\n' +
                             'Classical algorith complexity is O(N) while quantum is O(square root of N).',
              'link': 'https://en.wikipedia.org/wiki/Grover%27s_algorithm',
              'image': b'1010',
              'parameters': ['secret', 'secret'],
              'likes': 457,
              'enabled': True},
              
              ]
              
    
    with table.batch_writer(overwrite_by_pkeys=['id']) as batch:
        for item in items:
            batch.put_item(item)
         
            
# add_test_data()

# print("Test data added to 'm1-algorithms-table'")


def get_all_algorithms():
    
    response = table.scan()

    return response['Items']
    

def query_algorithms(query_parameters):

    # query_parameters = [{'filter': 'value'}]
    
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
    

def set_algorithm_state(algorithm_id, state):

    response = table.update_item(
        
        Key={'id': algorithm_id},
        UpdateExpression="SET enabled = :b",
        ExpressionAttributeValues={':b': state})

    status_code = response['ResponseMetadata']['HTTPStatusCode']
        
    return {'status_code': status_code}