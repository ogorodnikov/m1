import io
import pytest

from core.app import FlaskApp
from core.app import create_app

from core.main import Main
from core.dynamo import Dynamo
# from core.runner import Runner
from core.routes import Routes
# from core.cognito import Cognito
# from core.telegram import Bot
# from core.facebook import Facebook


###   Algorithms   ###

def test_get_algorithms(app):
    
    response = app.get('/algorithms')
    assert b'Algorithms' in response.data
    
    response = app.get('/algorithms?type=classical')
    assert b'Extended Euclidean' in response.data
    assert b'Bernstein Vazirani' not in response.data

    response = app.get('/algorithms?type=quantum')
    assert b'Extended Euclidean' not in response.data
    assert b'Bernstein Vazirani' in response.data
    
    response = app.get('/algorithms?test_filter_name=test_filter_value')
    assert b'Algorithms' in response.data
    
    
def test_get_algorithm(app):
    response = app.get('/algorithms/egcd')
    assert b'Extended Euclidean' in response.data


###   Fixtures   ###

@pytest.fixture(scope="module")
def app():
    
    test_app = create_app()
    test_app.testing = True
    test_app.secret_key = 'test_key'
    
    # db = Dynamo()
    # cognito = Cognito()
    # runner = Runner(db)
    # facebook = Facebook()
    # telegram_bot = Bot(db, runner)
    
    db = Dynamo()
    cognito = None
    runner = None
    facebook = None
    telegram_bot = None
    
    routes = Routes(db, test_app, cognito, runner, facebook, telegram_bot)
    
    test_context = test_app.test_request_context()
    test_context.push()
    
    with test_app.test_client() as app:
        yield app
    
    test_context.pop()