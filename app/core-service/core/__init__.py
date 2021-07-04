from flask import Flask
from flask_cors import CORS
from flask_awscognito import AWSCognitoAuthentication


from core import config

app = Flask(__name__)
app.config.from_object(config.Config)

CORS(app)

aws_auth = AWSCognitoAuthentication(app)

from core import routes