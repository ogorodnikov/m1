from flask import Flask
from flask_cors import CORS

from logging.config import dictConfig

from core import config


app = Flask(__name__)

dictConfig(config.LOGGING_CONFIG)

app.logger.info(f'INIT')

CORS(app)

app.config.from_object(config.Config)


# from core.gunicorn.app import GunicornApp

# gunicorn_app = GunicornApp(app)


from core import engine

runner = engine.Runner()
# runner.start()



# from core import telegram

# bot = telegram.Bot()
# bot.start()


config.clear_figures_folder(app)


from core import routes










