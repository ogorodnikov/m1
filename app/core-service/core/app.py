from flask import Flask
from flask_cors import CORS

import signal
from os import environ
from threading import enumerate as enumerate_threads

from logging.handlers import RotatingFileHandler

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
        
        # self.start_log_files()
        
        configuration = config.Config()
        
        self.config.from_object(configuration)
        
        CORS(self)
        
        self.db = dynamo.DB(self)
        
        runner = engine.Runner(self)
        runner.start()
        
        bot = telegram.Bot(self)
        bot.start()
        
        self.users = cognito.Cognito()
        
        self.fb = facebook.FB()

    
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
        
    
    def start_log_files(self):
    
        log_folder = self.static_folder + '/logs/'
        
        formatter = logging.Formatter(fmt="[%(asctime)s] %(levelname).1s %(module)6.6s | %(message)s", 
                                      datefmt="%Y-%m-%d %H:%M:%S")
        
        core_handler = RotatingFileHandler(log_folder + 'core.log', maxBytes=100000, backupCount=5)
        core_handler.setLevel(logging.DEBUG)
        core_handler.setFormatter(formatter)
        
        self.logger.addHandler(core_handler)
        
        gunicorn_handler = RotatingFileHandler(log_folder + 'gunicorn.log', maxBytes=10000, backupCount=1)
        gunicorn_handler.setLevel(logging.DEBUG)
        gunicorn_handler.setFormatter(formatter)
        
        gunicorn_log = logging.getLogger('gunicorn.error')
        gunicorn_log.addHandler(gunicorn_handler)


    def clear_figures_folder(self):
        
        figures_folder = os.path.join(self.static_folder, 'figures')
    
        for figure in os.listdir(figures_folder):
            if figure == 'README.md':
                continue
            os.remove(os.path.join(figures_folder, figure))


    def termination_handler(self, signal, frame):
      
        self.clear_figures_folder()
        
        print(f'APP termination_handler signal {signal}, {frame}')
        

app = FlaskApp(__name__)

from core import routes
