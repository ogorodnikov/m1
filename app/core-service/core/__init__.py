from flask import Flask
from flask_cors import CORS

from core import config

from logging.config import dictConfig


app = Flask(__name__)
CORS(app)

app.config.from_object(config.Config)

dictConfig(config.LOGGING_CONFIG)


from core import routes