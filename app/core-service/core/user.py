from core import app

from flask_login import UserMixin
from flask_login import LoginManager


login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    print("Loaded:", user_id)
    return user_id
    

class User(UserMixin):
    
    id = ''
    
    def __init__(self, id):
        print("ID:", id)
        # self.id = id
