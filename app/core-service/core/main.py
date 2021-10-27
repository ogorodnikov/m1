from core import app
from core import config
from core import routes
from core import dynamo
from core import runner
from core import telegram
from core import cognito
from core import facebook


class Main:

    def __init__(self, *args, **kwargs):
        
        self.app = app.FlaskApp(__name__)
        
        configuration = config.Config(log_file_path=self.app.log_file_path)
        
        self.app.config.from_object(configuration)
        
        self.db = dynamo.Dynamo(self.app)
        
        self.app.db = self.db
        
        self.runner = runner.Runner(self.app)
        self.start_runner()
        
        self.app.runner = self.runner
        
        self.telegram_bot = telegram.Bot(self.db, self.runner)
        self.start_telegram_bot()

        self.users = cognito.Cognito()
        
        self.app.users = self.users
        
        self.facebook = facebook.Facebook()
        
        self.app.facebook = self.facebook
        
        self.routes = routes.Routes(self.app)
        
        
    def start_telegram_bot(self):
        
        if self.telegram_bot:
            self.telegram_bot.start()
            self.app.config['TELEGRAM_BOT_STATE'] = 'Running'        

    def stop_telegram_bot(self):
        
        if self.telegram_bot:
            self.telegram_bot.stop()
            self.app.config['TELEGRAM_BOT_STATE'] = 'Stopped'    
            
    def start_runner(self):
        
        if self.runner:
            self.runner.start()
            self.app.config['RUNNER_STATE'] = 'Running'        

    def stop_runner(self):
        
        if self.runner:
            self.runner.stop()
            self.app.config['RUNNER_STATE'] = 'Stopped'         