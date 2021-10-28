import os
import logging

from logging.handlers import RotatingFileHandler

from core import app
from core import config
from core import routes
from core import dynamo
from core import runner
from core import telegram
from core import cognito
from core import facebook


class Main:

    def __init__(self, *args, **kwargs):
        
        self.config = config.Config()
        
        self.app = app.FlaskApp(__name__)
        self.app.config.from_object(self.config)
        
        self.start_logging(log_file_path=self.app.log_file_path)
        
        self.db = dynamo.Dynamo(self.app)
        self.app.db = self.db
        
        self.runner = runner.Runner(self.app)
        self.start_runner()
        self.app.runner = self.runner
        
        self.telegram_bot = telegram.Bot(self.db, self.runner)
        self.start_telegram_bot()

        self.users = cognito.Cognito()
        self.app.users = self.users
        
        self.facebook = facebook.Facebook()
        self.app.facebook = self.facebook
        
        self.routes = routes.Routes(self.db, self.app, self.users, self.runner, self.facebook)
        
        
        
    def start_telegram_bot(self):
        
        if self.telegram_bot:
            self.telegram_bot.start()
            self.app.config['TELEGRAM_BOT_STATE'] = 'Running'        

    def stop_telegram_bot(self):
        
        if self.telegram_bot:
            self.telegram_bot.stop()
            self.app.config['TELEGRAM_BOT_STATE'] = 'Stopped'    
            
    def start_runner(self):
        
        if self.runner:
            self.runner.start()
            self.app.config['RUNNER_STATE'] = 'Running'        

    def stop_runner(self):
        
        if self.runner:
            self.runner.stop()
            self.app.config['RUNNER_STATE'] = 'Stopped'
            
    
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
        
        root_logger.info("LOGGER initiated")