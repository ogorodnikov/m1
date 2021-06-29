from flask import Flask
from flask_cors import CORS

from flask_login import LoginManager



app = Flask(__name__)

CORS(app)

app.config['SECRET_KEY'] = 'acf3fc4f4c3fccfcafa24499'
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

from core import routes