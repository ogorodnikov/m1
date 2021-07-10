from flask import Flask
from flask_cors import CORS

from core import config

from logging.config import dictConfig


dictConfig(config.LOGGING_CONFIG)

print(config.LOGGING_CONFIG)

app = Flask(__name__)
app.config.from_object(config.Config)

CORS(app)


from core import routes