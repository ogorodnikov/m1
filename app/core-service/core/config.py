import os
import boto3
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()

cognito_client = boto3.client('cognito-idp')


def get_user_pool_id(user_pool):

    user_pool_response = cognito_client.list_user_pools(MaxResults=60)
    user_pools = user_pool_response['UserPools']
    user_pool_id = next(attribute['Id'] for attribute in user_pools
                        if attribute['Name'] == user_pool)
                        
    return user_pool_id
    

def get_user_pool_client_id(user_pool_id, user_pool_client):

    user_pool_clients_response = cognito_client.list_user_pool_clients(UserPoolId=user_pool_id,
                                                               MaxResults=60)
    user_pool_clients = user_pool_clients_response['UserPoolClients']
    user_pool_client_id = next(attribute['ClientId'] for attribute in user_pool_clients
                               if attribute['ClientName'] == user_pool_client)
                        
    return user_pool_client_id
    
    
user_pool = os.getenv('USER_POOL')
user_pool_id = get_user_pool_id(user_pool)

user_pool_client = os.getenv('USER_POOL_CLIENT')
user_pool_client_id = get_user_pool_client_id(user_pool_id, user_pool_client)

    
class Config(object):
    
    REGION = os.getenv('REGION')
    DOMAIN = os.getenv('DOMAIN')
    VERSION = os.getenv('VERSION')
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    COGNITO_USER_POOL_ID = user_pool_id
    COGNITO_USER_POOL_CLIENT_ID = user_pool_client_id

    FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')    
    FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')
    
    AWS_NLB = os.getenv('AWS_NLB')
    
    JSONIFY_PRETTYPRINT_REGULAR = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    