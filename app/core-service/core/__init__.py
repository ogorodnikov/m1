from flask import Flask
from flask_cors import CORS

from core import config


app = Flask(__name__)
app.config.from_object(config.Config)

CORS(app)


from core import routes