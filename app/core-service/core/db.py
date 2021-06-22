import boto3, json

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('m1-algorithms-table')

items = [{'id': 'bernvaz',
          'name': 'Bernstein Vazirani',
          'type': 'quantum',
          'description': 'Determines hidden message encoded in black-box function.\n' +
                         'Classical algorith complexity is O(n) while quantum is O(1):\n' +
                         'https://en.wikipedia.org/wiki/Bernstein%E2%80%93Vazirani_algorithm',
          'image': 'b1010',
          'parameters': ['secret']},
          
          {'id': 'egcd',
          'name': 'Extended Euclidean',
          'type': 'classic',
          'description': 'Calculates GCD (Greatest common divisor) and Bézout coefficents.\n' +
                         'https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm',
          'image': 'b1010',
          'parameters': ['a', 'b']}]

with table.batch_writer(overwrite_by_pkeys=['id']) as batch:
    for item in items:
        batch.put_item(item)
        
        

def get_all_algorithms():
    
    response = table.scan()

    return json.dumps(response['Items'])

# query_parameters = {'filter': 'algorithm-type',
#                     'value': 'test_type'}