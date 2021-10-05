from flask import Flask
from flask_cors import CORS

from logging.config import dictConfig

from core import config
from core import dynamo
from core import engine
from core import telegram
from core import cognito
from core import facebook

import signal

from core.gunicorn.app import GunicornApp

from os import environ


class FlaskApp(Flask):
    
    def __init__(self, *args, **kwargs):
        
        signal.signal(signal.SIGHUP, self.termination_handler)        
        signal.signal(signal.SIGTERM, self.termination_handler)
        
        super().__init__(*args, **kwargs)
        
        dictConfig(config.LOGGING_CONFIG)
        
        self.config.from_object(config.Config)
        
        config.start_log_files(self)
        
        
        CORS(self)
        
        db = dynamo.DB(self)
        
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
        
        self.run(*args, **kwargs)
        
    
    def termination_handler(self, signal, frame):
      
        config.clear_figures_folder(self)
        
        print(f'APP termination_handler signal {signal}, {frame}')



app = FlaskApp(__name__)

from core import routes
