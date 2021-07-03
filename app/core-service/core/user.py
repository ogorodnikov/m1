from core import app

from flask_login import UserMixin
from flask_login import LoginManager


login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = u"Could you please login?"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(id):
    
    new_user = User(id, "cool")

    return new_user
    

class User(UserMixin):

    def __init__(self, id, name):
        self.id = id
        self.name = name
        
        print('Init:')
        print("  Instance ID:", self.id)
        print("  Instance Name:", self.name)
        
    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

