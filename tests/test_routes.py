import pytest

from flask import url_for

from core.app import create_app

from core.facebook import Facebook

from urllib.parse import urlencode



HOME_PAGE_PHRASE = 'M1 Core Service'

def attribute_error_wrapper(test_function):
    
    def inner_function(client, *args, **kwargs):
        
        with pytest.raises(AttributeError) as error:
            test_function(client, *args, **kwargs)
        assert "'NoneType' object has no attribute 'replace'" in str(error.value)
        
    return inner_function
    
    
def test_home(client):
    
    # print(f"url_for('home') {url_for('home')}")      
    # print(f"url_for('home') {url_for('home', _external=False)}")      
    # print(f"url_for('home') {url_for('home', _external=True)}")    
        
        
    response = client.get(url_for('home'))
    
    # print(f"response.data {response.data}")      
    
    assert b'M1 Core Service' in response.data


# def test_login(client):
#     response = client.get('/login')
#     assert b'Please sign in or register' in response.data
    

# def test_login_facebook(client):   
#     facebook_response = client.post('/login', data={'flow': 'facebook'})
#     assert b'Redirecting' in facebook_response.data

    
# @attribute_error_wrapper
# def test_login_code(client):
#     code_response = client.get('/login?code=dummy_code', follow_redirects=True)


# @attribute_error_wrapper
# def test_login_register(client):
#     register_response = client.post('/login', data={'flow': 'register'})


# @attribute_error_wrapper
# def test_login_sign_in(client):
#     sign_in_response = client.post('/login', data={'flow': 'sign-in'})


# @attribute_error_wrapper
# def test_logout(client):
#     sign_in_response = client.get('/logout')
  

# # Algorithms

# def test_get_algorithms(client):
    
#     response = client.get('/algorithms')
#     assert b'Algorithms' in response.data
    
#     response = client.get('/algorithms?type=classical')
#     assert b'Extended Euclidean' in response.data
#     assert b'Bernstein Vazirani' not in response.data

#     response = client.get('/algorithms?type=quantum')
#     assert b'Extended Euclidean' not in response.data
#     assert b'Bernstein Vazirani' in response.data
    
#     response = client.get('/algorithms?test_filter_name=test_filter_value')
#     assert b'Algorithms' in response.data
    
    
# def test_get_algorithm(client):
#     response = client.get('/algorithms/egcd')
#     assert b'Extended Euclidean' in response.data
    
    
# @attribute_error_wrapper
# def test_like_algorithm(client):
#     response = client.get('/algorithms/egcd/like')


# # @attribute_error_wrapper
# def test_run_algorithm(client):
#     ...
    



def test_mocking(client, monkeypatch):
    
    def mock_get_autorization_url(self, login_url):
        return url_for('home')
    
    monkeypatch.setattr(Facebook, "get_autorization_url", mock_get_autorization_url)
    
    facebook_response = client.post('/login', data={'flow': 'facebook'}, follow_redirects=True)
    
    print(f"facebook_response.data {facebook_response.data}")
    
    assert HOME_PAGE_PHRASE in facebook_response.data.decode('utf-8')
 

###   Fixtures   ###           

@pytest.fixture(scope="module")
def client():
    

    
    app = create_app()
    app.testing = True
    
    test_context = app.test_request_context()
    test_context.push()
    
    with app.test_client() as client:
        yield client
    
    test_context.pop()
    app.stop_runner()
    