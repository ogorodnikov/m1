import boto3, json


dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('m1-algorithms-table')


items = [{'id': 'bernvaz',
          'name': 'Bernstein Vazirani',
          'type': 'quantum',
          'description': 'Determines hidden message encoded in black-box function.\n' +
                         'Classical algorith complexity is O(n) while quantum is O(1):\n' +
                         'https://en.wikipedia.org/wiki/Bernstein%E2%80%93Vazirani_algorithm',
          'image': '1010',
          'parameters': ['secret'],
          'likes': 0,
          'enabled': True},
          
          {'id': 'egcd',
          'name': 'Extended Euclidean',
          'type': 'classic',
          'description': 'Calculates GCD (Greatest common divisor) and Bézout coefficents.\n' +
                         'https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm',
          'image': '1010',
          'parameters': ['a', 'b'],
          'likes': 0,
          'enabled': True}]
          

with table.batch_writer(overwrite_by_pkeys=['id']) as batch:
    for item in items:
        batch.put_item(item)
        
        

def get_all_algorithms():
    
    response = table.scan()

    return json.dumps(response['Items'], indent=2, sort_keys=True)
    

def query_algorithms(query_parameters):

    # query_parameters = [{'filter': 'type', 'value': 'quantum'}]
    
    key_conditions = {}
    
    for query_parameter in query_parameters:
        
        filter_name = query_parameter['filter']
        filter_value = query_parameter['value']
    
        key_conditions[filter_name] = {'AttributeValueList': [filter_value], 
                                       'ComparisonOperator': "EQ"}
    
    response = table.query(IndexName='type-index',
                           KeyConditions=key_conditions)
    
    return json.dumps(response['Items'], indent=2, sort_keys=True)


def get_algorithm(algorithm_id):

    response = table.get_item(Key={'id': algorithm_id})
    
    return json.dumps(response['Item'], indent=2, sort_keys=True)


def like_algorithm(algorithm_id):

    response = table.update_item(
        
        Key={'id': algorithm_id},
        UpdateExpression="SET likes = likes + :n",
        ExpressionAttributeValues={':n': 1})
        
    status_code = response['ResponseMetadata']['HTTPStatusCode']
        
    return json.dumps({'status_code': status_code})
    

def set_algorithm_state(algorithm_id, state):

    response = table.update_item(
        
        Key={'id': algorithm_id},
        UpdateExpression="SET enabled = :b",
        ExpressionAttributeValues={':b': state})

    status_code = response['ResponseMetadata']['HTTPStatusCode']
        
    return json.dumps({'status_code': status_code})