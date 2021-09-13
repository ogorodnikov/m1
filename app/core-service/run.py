# from core import app
# app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=True, reloader_type='stat')



from gunicorn.app.base import BaseApplication
from gunicorn.workers.sync import SyncWorker

from flask import Flask


if __name__ == '__main__':
    
    class CustomWorker(SyncWorker):
        
        def handle_quit(self, sig, frame):
            self.app.application.stop(sig)
            super().handle_quit(sig, frame)
    
        def run(self):
            self.app.application.start()
            super().run()


    class GunicornApp(BaseApplication):

        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()
    
        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key.lower(), value)
    
            # self.cfg.set('worker_class', 'sample.__main__.CustomWorker')
    
        def load(self):
            return self.application
        
    app = Flask(__name__)
    gunicorn_app = GunicornApp(app)

    gunicorn_app.run()
        