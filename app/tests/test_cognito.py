import pytest

from core import cognito


# def test_users_init(client):
    
#     assert client.users
    
    
def test_root_route(test_app):
    
    response = test_app.get('/')
    
    assert b'M1 Core Service' in response.data


def test_home_route(test_app):
    
    response = test_app.get('/home')
    
    assert b'M1 Core Service' in response.data
    
        
    
# def test_login_user(test_app):

#     login_form = dict((('username', 'test'), ('password', '111111'), ('flow', 'sign-in')))
    
#     with test_app.app_context():
    
#         test_app.users.login_user(login_form)


@pytest.fixture(scope="session")
def app():
    
    from core.app import app
    
    yield app


@pytest.fixture(scope="session")
def test_app(app):
    
    app.testing = True
    
    with app.test_client() as test_app:
        yield test_app
