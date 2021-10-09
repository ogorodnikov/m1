import sys
import pytest

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
    
    
def test_login_user_fail(users):
    
    login_form = dict((
        ('username', 'test777'), 
        ('password', '777111'), 
        ('remember_me', 'True'), 
        ('flow', 'sign-in')
    ))
    
    with pytest.raises(Exception) as exception:

        users.login_user(login_form)
    
    assert "UserNotFoundException" in str(exception.value)
    

def test_log(users, capture_stdout):
    
    message = "Test log)"
    
    users.log(message)
    
    assert capture_stdout["stdout"] == 'COGNITO >>> ' + message + '\n'

    
@pytest.fixture(scope="session")
def users():
    
    users = cognito.Users()
    
    yield users
    

@pytest.fixture
def capture_stdout(monkeypatch):
    
    buffer = {"stdout": ""}

    def capture(message):
        buffer["stdout"] += message

    monkeypatch.setattr(sys.stdout, 'write', capture)
    
    return buffer