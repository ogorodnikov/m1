from flask import Flask
from flask_cors import CORS

from logging.config import dictConfig

from core import config
from core import dynamo
from core import engine
from core import telegram

import signal


def termination_handler(signal, frame):
  
  config.clear_figures_folder(app)
  
  print(f'INIT termination_handler signal {signal}, {frame}')

signal.signal(signal.SIGTERM, termination_handler)
signal.signal(signal.SIGHUP, termination_handler)



app = Flask(__name__)
    
dictConfig(config.LOGGING_CONFIG)

app.logger.info(f'INIT')

CORS(app)

app.config.from_object(config.Config)



db = dynamo.DB(app)

runner = engine.Runner(app)
runner.start()

bot = telegram.Bot(app)
bot.start()


from core import routes


from core.gunicorn.app import GunicornApp
gunicorn_app = GunicornApp(app)






