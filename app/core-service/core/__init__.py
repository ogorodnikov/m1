from flask import Flask
from flask_cors import CORS

from os import environ

from logging.config import dictConfig

from core import config


dictConfig(config.LOGGING_CONFIG)

app = Flask(__name__)




if not environ.get('WERKZEUG_RUN_MAIN'):
    
    app.logger.info(f'environ.get"(WERKZEUG_RUN_MAIN"): {environ.get("WERKZEUG_RUN_MAIN")}')
    



else:
    
    app.logger.info(f'environ.get("WERKZEUG_RUN_MAIN"): {environ.get("WERKZEUG_RUN_MAIN")}')
    
    CORS(app)

    app.config.from_object(config.Config)
    
    from core import engine
    
    runner = engine.Runner()
    
    from core import telegram
    
    bot = telegram.Bot()
    bot.start()
    
    config.clear_figures_folder(app)
    

    from core import routes