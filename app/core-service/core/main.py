import logging

from logging.handlers import RotatingFileHandler

from .app import FlaskApp
from .config import Config
from .routes import Routes
from .dynamo import Dynamo
from .runner import Runner
from .cognito import Cognito
from .telegram import Bot
from .facebook import Facebook


class Main:

    def __init__(self):

        self.config = Config()
        
        self.app = FlaskApp(__name__)
        self.app.config.from_object(self.config)
        
        self.start_logging(log_to_file=False)
        
        self.db = Dynamo()
        
        self.runner = Runner(self.db)
        self.runner.start()
        
        self.telegram_bot = Bot(self.db, self.runner)
        self.telegram_bot.start()

        self.cognito = Cognito()
        
        self.facebook = Facebook()
        
        self.routes = Routes(self.db, self.app, self.cognito, self.runner, 
                             self.facebook, self.telegram_bot)
            
    def start_logging(self, log_to_file=False, log_file_path=None):
        
        log_file_path = log_file_path or self.app.static_folder + '/logs'
        
        log_file = log_file_path + '/core.log'

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
        
        ibmq_logger = logging.getLogger('qiskit.providers.ibmq')
        ibmq_logger.setLevel(logging.INFO)
        ibmq_logger.handlers.clear()
        ibmq_logger.addHandler(console_handler)
        
        if log_to_file:
        
            file_formatter = logging.Formatter(fmt=file_format, datefmt=date_format)
            
            file_handler = RotatingFileHandler(
                log_file, 
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

        root_logger.info(f"LOGGER initiated")
