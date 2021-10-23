from gunicorn.workers.sync import SyncWorker
from gunicorn.app.base import BaseApplication, Application


class GunicornApp(Application):

    def __init__(self, app, options=None):
        
        self.options = options or {}
        self.application = app
        
        super().__init__()
        
        self.load_config_from_module_name_or_filename('python:core.gunicorn.config')
        # self.load_config_from_module_name_or_filename('/home/ec2-user/environment/m1/app/core-service/core/gunicorn/config.py')
        

    def load_config(self):
        
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        
        return self.application
        

class CustomWorker(SyncWorker):
        
    def handle_quit(self, sig, frame):
        
        app.logger.info(f'INIT handle_quit {self, sig, frame}')
        
        # self.app.application.stop(sig)
        
        super().handle_quit(sig, frame)

    def run(self):
        
        app.logger.info(f'INIT run {self}')
        
        # self.app.application.start()
        
        super().run()
        
        
        
        
        
# from gunicorn.app.wsgiapp import WSGIApplication
 
# wsgi_app = WSGIApplication()
# wsgi_app.app_uri = 'core:app'
 
# wsgi_app.run()