from flask import Flask
from flask_cors import CORS

from os import environ

from logging.config import dictConfig

from core import config

import time


app = Flask(__name__)

dictConfig(config.LOGGING_CONFIG)

app.logger.info(f'INIT Werkzeug run main: {environ.get("WERKZEUG_RUN_MAIN")}')


if environ.get('WERKZEUG_RUN_MAIN') or True:

    CORS(app)

    app.config.from_object(config.Config)
    
    from core import engine
    
    runner = engine.Runner()
    
    from core import telegram
    
    bot = telegram.Bot()
    bot.start()
    
    config.clear_figures_folder(app)
    

    from core import routes