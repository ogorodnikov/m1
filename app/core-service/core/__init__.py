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

# runner = None

from core import telegram

bot = telegram.Bot()
bot.start()

config.clear_figures_folder(app)


from core import routes






from core.gunicorn.app import GunicornApp

gunicorn_app = GunicornApp(app)

gunicorn_app.load_config_from_module_name_or_filename('python:core.gunicorn.config')


