import os
import boto3
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()

cognito_client = boto3.client('cognito-idp')
elb_client = boto3.client('elbv2')


def get_nlb_dns(nlb_name):
    
    load_balancers_response = elb_client.describe_load_balancers(Names=[nlb_name])
    
    load_balancers = load_balancers_response['LoadBalancers']
    
    nlb_dns = next(load_balancer['DNSName'] for load_balancer in load_balancers
                   if load_balancer['LoadBalancerName'] == nlb_name)
                        
    return nlb_dns


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
    
    
nlb_name = os.getenv('NLB_NAME')
nlb_dns = get_nlb_dns(nlb_name)
    
user_pool = os.getenv('USER_POOL')
user_pool_id = get_user_pool_id(user_pool)

user_pool_client = os.getenv('USER_POOL_CLIENT')
user_pool_client_id = get_user_pool_client_id(user_pool_id, user_pool_client)

    
class Config():
    
    REGION = os.getenv('REGION')
    DOMAIN = os.getenv('DOMAIN')
    VERSION = os.getenv('VERSION')
    SECRET_KEY = os.getenv('SECRET_KEY')
    TASK_ROLLOVER_SIZE = int(os.getenv('TASK_ROLLOVER_SIZE'))
    
    COGNITO_USER_POOL_ID = user_pool_id
    COGNITO_USER_POOL_CLIENT_ID = user_pool_client_id
    
    TASKS_TABLE_NAME = os.getenv('TASKS_TABLE_NAME')
    ALGORITHMS_TABLE_NAME = os.getenv('ALGORITHMS_TABLE_NAME')

    FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')    
    FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')
    
    AWS_NLB = nlb_dns
    
    TASK_TIMEOUT = 300
    QUEUE_WORKERS_PER_RUNNER = 1
    BACKEND_AVOID_LIST = ['ibmq_bogota']
    
    JSONIFY_PRETTYPRINT_REGULAR = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    CPU_COUNT = os.cpu_count()
    
    QISKIT_TOKEN = os.getenv('QISKIT_TOKEN')
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    

LOGGING_CONFIG = {'version': 1,

                  'formatters': 
                      {
                          'default': {
                                              'format': '%(levelname).1s %(module)6.6s | %(message)s'}},
                                            #   'format': '[%(asctime)s] %(module)6.6s | %(levelname).4s | %(message)s', 
                                            #   'datefmt': "%Y-%m-%d %H:%M:%S"}},
                                            
                  'handlers': 
                      {
                      'wsgi': {
                          'class': 'logging.StreamHandler',
                          'stream': 'ext://flask.logging.wsgi_errors_stream',
                          'formatter': 'default'
                      }
                  },
                                       
                  'root': {'level': 'INFO',
                          'handlers': ['wsgi']},
                        }


def clear_figures_folder(app):
    
    figures_folder = os.path.join(app.static_folder, 'figures')

    for figure in os.listdir(figures_folder):
        if figure == 'README.md':
            continue
        os.remove(os.path.join(figures_folder, figure))