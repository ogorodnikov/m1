import boto3
import json
import logging

dynamodb_client = boto3.client('dynamodb')


def response_to_dict(response):
    
    logging.info(response["Items"])
    
    algo_dict = {}
    
    # print("Response:", response)
    
    for item in response["Items"]:
        
        # print("    Item:", item)
        
        algo = {}
        algo["algorithm-id"] = item["algorithm-id"]["S"]
        algo["algorithm-type"] = item["algorithm-type"]["S"]
        
        # algo["algorithm-code"] = item["algorithm-code"]["S"]
        # algo["algorithm-image"] = item["algorithm-image"]["B"]
        
        # algo["likes"] = int(item["likes"]["N"])
        # algo["enabled"] = item["enabled"]["BOOL"]

        algo_dict["algorithms"] = []
        algo_dict["algorithms"].append(algo)
        
    return algo_dict
    

def get_all_algorithms():

    response = dynamodb_client.scan(TableName='m1-algorithms-table')
    
    algo_dict = response_to_dict(response)

    return json.dumps(algo_dict)
    

def query_algorithms(query_parameters):

    logging.info(json.dumps(query_parameters))
    
    filter_name = query_parameters['filter']
    filter_value = query_parameters['value']

    response = dynamodb_client.query(
        TableName='m1-algorithms-table',
        IndexName=filter_name+'-index',
        KeyConditions={filter_name: {'AttributeValueList': [{'S': filter_value}], 
                                     'ComparisonOperator': "EQ"}})

    algo_dict = response_to_dict(response)
    
    return json.dumps(algo_dict)


def get_algorithm(algorithm_id):

    response = dynamodb_client.get_item(TableName='m1-algorithms-table',
                                        Key={'algorithm-id': {'S': algorithm_id}})

    item = response["Item"]

    algo = {}
    algo["algorithm-id"] = item["algorithm-id"]["S"]
    algo["algorithm-type"] = item["algorithm-type"]["S"]
    
    # algo["algorithm-code"] = item["algorithm-code"]["S"]
    # algo["algorithm-image"] = item["algorithm-image"]["B"]
    
    # algo["likes"] = int(item["likes"]["N"])
    # algo["enabled"] = item["enabled"]["BOOL"]
    
    return json.dumps(algo)


def like_algorithm(algorithm_id):

    response = dynamodb_client.update_item(
        
        TableName='m1-algorithms-table',
        Key={'algorithm-id': {'S': algorithm_id}},
        UpdateExpression="SET likes = likes + :n",
        ExpressionAttributeValues={':n': {'N': '1'}})

    status = {}
    status["update_status"] = "success";

    return json.dumps(status)


def set_algorithm_state(algorithm_id, state):

    response = client.update_item(
        
        TableName='m1-algorithms-table',
        Key={'algorithm-id': {'S': algorithm_id}},
        UpdateExpression="SET enabled = :b",
        ExpressionAttributeValues={':b': {'BOOL': state}})

    status = {}
    status["update_status"] = "success";

    return json.dumps(status)


if __name__ == "__main__":
    
    assert get_all_algorithms()
    
    query_parameters = {'filter': 'algorithm-type',
                        'value': 'test_type'}
    
    assert query_algorithms(query_parameters)
    