import os
import boto3
import logging

from dotenv import load_dotenv
from datetime import timedelta

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

        self.QISKIT_TOKEN = os.getenv('QISKIT_TOKEN')
        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        
        self.NLB_NAME = os.getenv('NLB_NAME')
        self.AWS_NLB = self.get_nlb_dns(self.NLB_NAME)
        os.environ['AWS_NLB'] = self.AWS_NLB
      
        self.TASK_TIMEOUT = 300
        self.QUEUE_WORKERS_PER_RUNNER = 1
        self.BACKEND_AVOID_LIST = ['ibmq_bogota']
        
        self.JSONIFY_PRETTYPRINT_REGULAR = False
        self.PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
        self.CPU_COUNT = os.cpu_count()
        
        # self.EXPLAIN_TEMPLATE_LOADING = True
        
        self.LOG_FILE_PATH = kwargs.get('log_file_path')
        
        self.start_logging(self.LOG_FILE_PATH)
        
    
    def start_logging(self, log_file_path=None):

        short_format = "%(levelname).1s %(module)6.6s | %(message)s"
        long_format = "[%(asctime)s] %(module)6.6s | %(levelname).4s | %(message)s"
        file_format = "[%(asctime)s] %(levelname).1s %(module)6.6s | %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        
        console_formatter = logging.Formatter(fmt=short_format, datefmt=date_format)
                                  
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
        
        if log_file_path:
        
            file_formatter = logging.Formatter(fmt=file_format, datefmt=date_format)
            
            file_handler = RotatingFileHandler(
                log_file_path, 
                maxBytes=100000, 
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            
            gunicorn_error_logger = logging.getLogger('gunicorn.error')
            gunicorn_access_logger = logging.getLogger('gunicorn.access')
    
            root_logger.addHandler(file_handler)        
            gunicorn_error_logger.addHandler(file_handler)
            gunicorn_access_logger.addHandler(file_handler)
        
        root_logger.info("LOGGING initiated")
        

    def get_nlb_dns(self, nlb_name):
        
        load_balancers_response = self.elb_client.describe_load_balancers(Names=[nlb_name])
        
        load_balancers = load_balancers_response['LoadBalancers']
        
        nlb_dns = next(load_balancer['DNSName'] for load_balancer in load_balancers
                       if load_balancer['LoadBalancerName'] == nlb_name)
                            
        return nlb_dns
        

    def print_environ(self):
    
        for key, value in sorted(os.environ.items()):
            print(f"{key}: {value}")