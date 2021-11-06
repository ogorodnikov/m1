import os
import signal

from flask import Flask
from flask_cors import CORS

from core.gunicorn.app import GunicornApp


class FlaskApp(Flask):
    
    def __init__(self, *args, **kwargs):
        
        signal.signal(signal.SIGHUP, self.termination_handler)        
        signal.signal(signal.SIGTERM, self.termination_handler)
        
        super().__init__(*args, **kwargs)
        
        CORS(self)


    def run_with_gunicorn(self, *args, **kwargs):
        
        gunicorn_app = GunicornApp(self)
        
        test_mode = kwargs.get('test_mode')
        
        gunicorn_app.run(*args, **kwargs)

        
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

        self.run(*args, **kwargs)
        
    
    def clear_figures_folder(self):
        
        figures_folder = os.path.join(self.static_folder, 'figures')
        
        for filename in os.listdir(figures_folder):
            if filename == 'README.md':
                continue
            os.remove(os.path.join(figures_folder, filename))


    def termination_handler(self, signal, frame):
      
        self.clear_figures_folder()
        
        print(f'APP termination_handler signal {signal}, {frame}')
        
        
    def exit_application(self, test_mode=False):
        
        print(f'APP exit_application')
        
        os._exit(0) if not test_mode else None
        

def create_app():
    
    app = FlaskApp(__name__)
    
    return app
