import os
import boto3
from dotenv import load_dotenv
from datetime import timedelta


VERSION = 'V.0.20.1'
DEFAULT_REGION = 'us-east-1'
COGNITO_DOMAIN = 'auth.ogoro.me'

USER_POOL = 'm1-user-pool'
USER_POOL_CLIENT = 'm1-user-pool-client'
USER_POOL_CLIENT_SECRET = ''


cognito_client = boto3.client('cognito-idp')


def get_user_pool_id(user_pool):

    user_pool_response = cognito_client.list_user_pools(MaxResults=60)
    user_pools = user_pool_response['UserPools']
    user_pool_id = next(attribute['Id'] for attribute in user_pools
                        if attribute['Name'] == user_pool)
                        
    return user_pool_id
    

def get_user_pool_clients(user_pool_id):

    user_pool_clients_response = cognito_client.list_user_pool_clients(UserPoolId=user_pool_id,
                                                               MaxResults=60)
    user_pool_clients = user_pool_clients_response['UserPoolClients']
    user_pool_client_id = next(attribute['ClientId'] for attribute in user_pool_clients
                               if attribute['ClientName'] == USER_POOL_CLIENT)
                        
    return user_pool_client_id
    

user_pool_id = get_user_pool_id(USER_POOL)
user_pool_client_id = get_user_pool_clients(user_pool_id)

    
class Config(object):
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    VERSION = VERSION
    AWS_DEFAULT_REGION = DEFAULT_REGION
    AWS_COGNITO_DOMAIN = COGNITO_DOMAIN
    AWS_COGNITO_USER_POOL_ID = user_pool_id
    AWS_COGNITO_USER_POOL_CLIENT_ID = user_pool_client_id
    AWS_COGNITO_USER_POOL_CLIENT_SECRET = USER_POOL_CLIENT_SECRET
    
    FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')    
    FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')
    
    JSONIFY_PRETTYPRINT_REGULAR = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)