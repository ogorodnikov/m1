from flask import Flask
from flask_cors import CORS

from os import environ
from logging.config import dictConfig

from core import config



dictConfig(config.LOGGING_CONFIG)

app = Flask(__name__)


# from core import runner


if environ.get('WERKZEUG_RUN_MAIN') == 'true':
    
    app.logger.info(f'INIT Werkzeug Main')
    
    CORS(app)

    app.config.from_object(config.Config)
    
    from core import runner, telegram
    
    runner.start_task_worker_processes()
    
    telegram.Bot()
    


from core import routes