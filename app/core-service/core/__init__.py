from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

app.config['SECRET_KEY'] = 'acf3fc4f4c3fccfcafa24499'
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

from core import routes