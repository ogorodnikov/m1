from flask import Flask
from flask_cors import CORS

import signal
from os import environ
from threading import enumerate as enumerate_threads

from logging.config import dictConfig

from core import config
from core import dynamo
from core import engine
from core import telegram
from core import cognito
from core import facebook

from core.gunicorn.app import GunicornApp


class FlaskApp(Flask):
    
    def __init__(self, *args, **kwargs):
        
        signal.signal(signal.SIGHUP, self.termination_handler)        
        signal.signal(signal.SIGTERM, self.termination_handler)
        
        super().__init__(*args, **kwargs)
        
        dictConfig(config.LOGGING_CONFIG)
        
        self.config.from_object(config.Config)
        
        # config.start_log_files(self)
        
        
        CORS(self)
        
        self.db = dynamo.DB(self)
        
        runner = engine.Runner(self)
        runner.start()
        
        bot = telegram.Bot(self)
        bot.start()
        
        users = cognito.Users(self)
        fb = facebook.FB(self)

    
    def run_with_gunicorn(self, *args, **kwargs):
        
        gunicorn_app = GunicornApp(self)
        
        gunicorn_app.run(*args, **kwargs)

        
    def run_with_developement_server(self, *args, **kwargs):
        
        developement_server_parameters = {
            'host': "0.0.0.0", 
            'port': 8080, 
            'debug': True, 
            'use_reloader': False, 
            'reloader_type': 'stat'
        }
        
        kwargs.update(**developement_server_parameters)

        self.run(*args, **kwargs)
        
    
    def termination_handler(self, signal, frame):
      
        config.clear_figures_folder(self)
        
        print(f'APP termination_handler signal {signal}, {frame}')



app = FlaskApp(__name__)

# app.launch = app.run_with_gunicorn

app.launch = app.run_with_developement_server

from core import routes
