from flask import Flask
from flask_cors import CORS

from core import config

from logging.config import dictConfig

from yaml import load


# logging_config = load(open('logging_config.yml'))

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(module)6.6s | %(levelname).4s | %(message)s', 
        
        # 'format': '[%(asctime)s] %(module)6.6s | %(levelname).4s | %(message)s', 
        # 'datefmt': "%Y-%m-%d %H:%M:%S",
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)
app.config.from_object(config.Config)

# logging_config = 
# logging.config.dictConfig(config)

app.logger.setLevel(20) # INFO


CORS(app)


from core import routes