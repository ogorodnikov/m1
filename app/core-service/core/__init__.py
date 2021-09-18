from flask import Flask
from flask_cors import CORS

from logging.config import dictConfig

from core import config
from core import dynamo
from core import engine
from core import telegram


app = Flask(__name__)
    
dictConfig(config.LOGGING_CONFIG)

app.logger.info(f'INIT')

CORS(app)

app.config.from_object(config.Config)



db = dynamo.DB(app)

runner = engine.Runner(app)
runner.start()

bot = telegram.Bot(app)
bot.start()


config.clear_figures_folder(app)

from core import routes


# from core.gunicorn.app import GunicornApp
# gunicorn_app = GunicornApp(app)






