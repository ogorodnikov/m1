from flask import Flask
from flask_cors import CORS

from os import environ
from logging.config import dictConfig

from core import config

from threading import enumerate as e


from time import sleep


dictConfig(config.LOGGING_CONFIG)

app = Flask(__name__)


# from core import runner


if environ.get('WERKZEUG_RUN_MAIN') == 'true':
    
    app.logger.info(f'INIT Werkzeug Main')
    
    CORS(app)

    app.config.from_object(config.Config)
    
    from core import runner
    
    runner.start_task_worker_processes()
    
    
    
    # from core import telegram
    
    # telegram.start_bot_polling()
    
    # app.logger.info(f'e(): {e()}')
    
    # sleep(5)
    
    # telegram.bot.stop_bot()
    
    # app.logger.info(f'Stop')
    # app.logger.info(f'e(): {e()}')
    
    # sleep(5)
    
    # telegram.start_bot_polling()
    
    # app.logger.info(f'Restart')
    # app.logger.info(f'e(): {e()}')


from core import routes