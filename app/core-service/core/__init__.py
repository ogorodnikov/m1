from flask import Flask
from flask_cors import CORS

from os import environ

from logging.config import dictConfig

from core import config

import time


app = Flask(__name__)

dictConfig(config.LOGGING_CONFIG)

app.logger.info(f'INIT')

CORS(app)

app.config.from_object(config.Config)

from core import engine

runner = engine.Runner()

from core import telegram

bot = telegram.Bot()
bot.start()

config.clear_figures_folder(app)


from core import routes
    


from gunicorn.app.base import BaseApplication
from gunicorn.workers.sync import SyncWorker


class CustomWorker(SyncWorker):
        
    def handle_quit(self, sig, frame):
        
        app.logger.info(f'INIT handle_quit {self, sig, frame}')
        
        # self.app.application.stop(sig)
        super().handle_quit(sig, frame)

    def run(self):
        
        app.logger.info(f'INIT run {self}')
        
        # self.app.application.start()
        super().run()


print(CustomWorker)


class GunicornApp(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

        # self.cfg.set('worker_class', 'core.CustomWorker')

    def load(self):
        return self.application

gunicorn_options = {'bind': '0.0.0.0:8080',
                    'accesslog': '-',
                    'access_log_format': "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs",
                    'workers': 1,
                    'threads': 1,
                    'reload': 'true',
                    # 'daemon': 'true',
                   }

gunicorn_app = GunicornApp(app, gunicorn_options)


        
    