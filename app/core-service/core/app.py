import os
import signal

from flask import Flask
from flask_cors import CORS

from threading import enumerate as enumerate_threads

from core import config
from core import routes
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
        
        # log_file_path = self.static_folder + '/logs/core.log'
        log_file_path = None
        
        configuration = config.Config(log_file_path=log_file_path)
        
        self.config.from_object(configuration)
        
        CORS(self)
        
        self.db = dynamo.DB(self)
        
        self.runner = engine.Runner(self)
        self.start_runner()
        
        self.telegram_bot = telegram.Bot(self.db, self.runner)
        self.start_telegram_bot()

        self.users = cognito.Cognito()
        
        self.facebook = facebook.Facebook()
        
        self.routes = routes.Routes(self)
        
        
    def start_telegram_bot(self):
        
        if self.telegram_bot:
            self.telegram_bot.start()
            self.config['TELEGRAM_BOT_STATE'] = 'Running'        

    def stop_telegram_bot(self):
        
        if self.telegram_bot:
            self.telegram_bot.stop()
            self.config['TELEGRAM_BOT_STATE'] = 'Stopped'    
            
    def start_runner(self):
        
        if self.runner:
            self.runner.start()
            self.config['RUNNER_STATE'] = 'Running'        

    def stop_runner(self):
        
        if self.runner:
            self.runner.stop()
            self.config['RUNNER_STATE'] = 'Stopped'                

    
    def run_with_gunicorn(self, *args, **kwargs):
        
        gunicorn_app = GunicornApp(self)
        
        test_mode = kwargs.get('test_mode')
        
        gunicorn_app.run(*args, **kwargs) if not test_mode else None

        
    def run_with_development_server(self, *args, **kwargs):
        
        development_server_parameters = {
            'host': "0.0.0.0", 
            'port': 8080, 
            'debug': True, 
            'use_reloader': False, 
            'reloader_type': 'stat'
        }
        
        kwargs.update(**development_server_parameters)
        
        test_mode = kwargs.get('test_mode')

        self.run(*args, **kwargs) if not test_mode else None
        
    
    def clear_figures_folder(self):
        
        figures_folder = os.path.join(self.static_folder, 'figures')
    
        for figure in os.listdir(figures_folder):
            if figure == 'README.md':
                continue
            os.remove(os.path.join(figures_folder, figure))


    def termination_handler(self, signal, frame):
      
        self.clear_figures_folder()
        
        print(f'APP termination_handler signal {signal}, {frame}')
        
        
    def exit_application(self, test_mode=False):
        
        print(f'APP exit_application')
        
        os._exit(0) if not test_mode else None
        

def create_app():
    
    app = FlaskApp(__name__)
    
    return app
