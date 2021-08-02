from flask import Flask
from flask_cors import CORS

from os import environ
from logging.config import dictConfig

from core import config


app = Flask(__name__)
CORS(app)


from core import runner


if environ.get('WERKZEUG_RUN_MAIN') != 'true':
    
    print('Werkzeug main == FALSE')
    
else:
    
    print('Werkzeug main == TRUE')
    
    app.config.from_object(config.Config)
    
    print('++++ APP:', app)
        
    print('++++ Config loaded:')

    print(app.config)   
    
    dictConfig(config.LOGGING_CONFIG)
    
    runner.start_task_worker_threads()
    

from core import routes