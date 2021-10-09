# import pytest


# def test_root_route(test_app):
    
#     response = test_app.get('/')
    
#     assert b'M1 Core Service' in response.data


# def test_home_route(test_app):
    
#     response = test_app.get('/home')
    
#     assert b'M1 Core Service' in response.data


# @pytest.fixture(scope="session")
# def app():
    
#     from core.app import app
    
#     yield app


# @pytest.fixture(scope="session")
# def test_app(app):
    
#     app.testing = True
    
#     with app.test_client() as test_app:
#         yield test_app
