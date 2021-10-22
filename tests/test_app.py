import pytest

# from core.app import app

from core.app import FlaskApp


def test_home(client):

    response = client.get('/')
    
    print(response)
    print(response.data)
    
    assert b'M1 Core Service' in response.data



@pytest.fixture(scope="module")
def client():
    
    app = FlaskApp(__name__)
    app.testing = True
    
    with app.test_client() as client:
        yield client
        
    # app.exit_application()
    