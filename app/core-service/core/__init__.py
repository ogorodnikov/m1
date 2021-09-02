from flask import Flask
from flask_cors import CORS

from os import environ

from logging.config import dictConfig

from core import config


dictConfig(config.LOGGING_CONFIG)

app = Flask(__name__)

app.logger.info(f'INIT WERKZEUG_RUN_MAIN')


if environ.get('WERKZEUG_RUN_MAIN') == 'true':
    
    app.logger.info(f'INIT WERKZEUG_RUN_MAIN == True')
    
    CORS(app)

    app.config.from_object(config.Config)
    
    from core import run, telegram
    
    runner = run.Runner()
    
    bot = telegram.Bot()
    bot.start()
    
    config.clear_figures_folder(app)
    

from core import routes