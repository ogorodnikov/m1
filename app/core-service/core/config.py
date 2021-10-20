import os
import boto3
from dotenv import load_dotenv
from datetime import timedelta

import logging
from logging.handlers import RotatingFileHandler


class Config():
    
    def __init__(self, *args, **kwargs):
        
        load_dotenv()

        self.elb_client = boto3.client('elbv2')
        
        self.REGION = os.getenv('REGION')
        self.DOMAIN = os.getenv('DOMAIN')
        self.VERSION = os.getenv('VERSION')
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.TASK_ROLLOVER_SIZE = int(os.getenv('TASK_ROLLOVER_SIZE'))
        
        self.TASKS_TABLE_NAME = os.getenv('TASKS_TABLE_NAME')
        self.ALGORITHMS_TABLE_NAME = os.getenv('ALGORITHMS_TABLE_NAME')
        
        self.CORE_BUCKET = os.getenv('CORE_BUCKET')
    
        self.FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')    
        self.FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')
        
        self.NLB_NAME = os.getenv('NLB_NAME')
        self.AWS_NLB = self.get_nlb_dns(self.NLB_NAME)
      
        self.TASK_TIMEOUT = 300
        self.QUEUE_WORKERS_PER_RUNNER = 1
        self.BACKEND_AVOID_LIST = ['ibmq_bogota']
        
        self.JSONIFY_PRETTYPRINT_REGULAR = False
        self.PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
        self.CPU_COUNT = os.cpu_count()
        
        self.QISKIT_TOKEN = os.getenv('QISKIT_TOKEN')
        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
        self.LOGGING_CONFIG = {'version': 1,
        
                                  'formatters': {
                                      'default': {
                                          'format': '%(levelname).1s %(module)6.6s | %(message)s'
                                        #   'format': '[%(asctime)s] %(module)6.6s | %(levelname).4s | %(message)s',
                                        #   'datefmt': "%Y-%m-%d %H:%M:%S"
                                      }
                                  },
                                                            
                                  'handlers': {
                                      'wsgi': {
                                          'class': 'logging.StreamHandler',
                                        #   'stream': 'ext://flask.logging.wsgi_errors_stream',
                                          'formatter': 'default'
                                      }
                                  },
                                                       
                                  'root': {
                                      'level': 'INFO',
                                      'handlers': ['wsgi']
                                  }
                                }


    def get_nlb_dns(self, nlb_name):
        
        load_balancers_response = self.elb_client.describe_load_balancers(Names=[nlb_name])
        
        load_balancers = load_balancers_response['LoadBalancers']
        
        nlb_dns = next(load_balancer['DNSName'] for load_balancer in load_balancers
                       if load_balancer['LoadBalancerName'] == nlb_name)
                            
        return nlb_dns
        

    def print_environ(self):
    
        for key, value in sorted(os.environ.items()):
            print(f"{key}: {value}")