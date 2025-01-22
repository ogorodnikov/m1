import os
import boto3

from dotenv import load_dotenv
from datetime import timedelta


class Config:
    
    def __init__(self):

        load_dotenv()

        self.elb_client = boto3.client('elbv2')

        self.REGION = os.getenv('REGION')
        self.DOMAIN = os.getenv('DOMAIN')
        self.VERSION = os.getenv('VERSION')
        self.SECRET_KEY = os.getenv('SECRET_KEY')

        self.CORE_BUCKET = os.getenv('CORE_BUCKET')        
        self.TASKS_TABLE_NAME = os.getenv('TASKS_TABLE_NAME')
        self.ALGORITHMS_TABLE_NAME = os.getenv('ALGORITHMS_TABLE_NAME')
    
        self.FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')    
        self.FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')

        self.QISKIT_TOKEN = os.getenv('QISKIT_TOKEN')
        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        
        self.NLB_NAME = os.getenv('NLB_NAME')
        self.AWS_NLB = self.get_nlb_dns(self.NLB_NAME)
        os.environ['AWS_NLB'] = self.AWS_NLB

        self.TASK_TIMEOUT = int(os.environ['TASK_TIMEOUT'])
        self.QUEUE_WORKERS_PER_RUNNER = int(os.environ['QUEUE_WORKERS_PER_RUNNER'])

        self.BACKEND_AVOID_STRING = 'ibmq_bogota'
        os.environ['BACKEND_AVOID_STRING'] = self.BACKEND_AVOID_STRING
        
        self.JSONIFY_PRETTYPRINT_REGULAR = False
        self.PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
        self.CPU_COUNT = os.cpu_count()
        
        # self.EXPLAIN_TEMPLATE_LOADING = True
        
        # self.QISKIT_IBMQ_PROVIDER_LOG_LEVEL = 'DEBUG'
        

    def get_nlb_dns(self, nlb_name):
        
        load_balancers_response = self.elb_client.describe_load_balancers(Names=[nlb_name])
        
        load_balancers = load_balancers_response['LoadBalancers']
        
        nlb_dns = next(load_balancer['DNSName'] for load_balancer in load_balancers
                       if load_balancer['LoadBalancerName'] == nlb_name)
                            
        return nlb_dns
