import sys
import pytest
import random

from core import config
from core import cognito



test_login_data = (
        
        (dict((('username', 'test'), ('password', '111111'), ('remember_me', 'True'), ('flow', 'sign-in'))), True),
        (dict((('username', 'test7'), ('password', '777777'), ('remember_me', 'True'), ('flow', 'sign-in'))), False)
        
    )


def test_users(users):
    
    assert users
    

def test_get_user_pool_id(users):
    
    user_pool = users.user_pool
    
    user_pool_id = users.get_user_pool_id(user_pool)
    
    # assert user_pool_id == "us-east-1_HhJBks0a8"
    assert len(user_pool_id) == 19
    

def test_get_client_id(users):
    
    user_pool_id = users.user_pool_id
    user_pool_client = users.user_pool_client
    
    client_id = users.get_client_id(user_pool_id, user_pool_client)

    # assert client_id == "1fhh6jkt6c8ji76vk9i04u5d9f"
    assert len(client_id) == 26
    

# @pytest.mark.parametrize("login_form, result", test_login_data)
# def test_login_user(users, login_form, result):
    
#     username = users.login_user(login_form)
#     assert bool(username) == result


def test_login_user_pass(users):
    
    login_form = dict((
        ('username', 'test'), 
        ('password', '111111'), 
        ('remember_me', 'True'), 
        ('flow', 'sign-in')
    ))
    
    assert users.login_user(login_form) == 'test'
    
    
def test_login_user_exception(users, test_user_form):
    
    login_form = test_user_form.update((
        ('remember_me', 'True'), 
        ('flow', 'sign-in')
    ))
    
    with pytest.raises(Exception) as exception:
    
        users.login_user(test_user_form)
    
    assert "UserNotFoundException" in str(exception.value)
    

def test_log(users, capture_output):
    
    message = "Test log :)"
    
    users.log(message)
    
    assert message in capture_output["stderr"]
    
    

# Register
    
def test_register_disable_delete_user(users, test_user_form):
    
    print(f"test_user_form {test_user_form}")
    
    users.register_user(test_user_form)
    # users.disable_user(test_user_form)
    users.delete_user(test_user_form)
    

def test_duplicate_register_user_exception(users, test_user_form):
    
    with pytest.raises(Exception) as exception:

        users.register_user(test_user_form)
        users.register_user(test_user_form)
    
    assert "UsernameExistsException" in str(exception.value)
    
    
    
###   Fixtures
    
@pytest.fixture(scope="module")
def users():
    
    configuration = config.Config()
    
    users = cognito.Cognito()
    
    yield users
    

@pytest.fixture
def test_user_form(users):
    
    user_index = random.randint(0, 1000)

    test_username = f"test_username_{user_index}"
    test_password = f"test_password_{user_index}"
    
    test_user_form = dict((('username', test_username), ('password', test_password)))
    
    yield test_user_form
    
    
# @pytest.fixture
# def test_user(users):
    
#     self.log(f'test_register_form: {test_register_form}')
    
#     users.register_user(test_register_form)

    
#     yield test_username, test_password
    
    
    
    

@pytest.fixture
def capture_output(monkeypatch):
    
    buffer = {"stderr": ""}

    def capture(message):
        buffer["stderr"] += message

    monkeypatch.setattr(sys.stderr, 'write', capture)

    return buffer