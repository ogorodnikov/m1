import pytest

from core.app import create_app
from core.dynamo import Dynamo
from core.runner import Runner
from core.cognito import Cognito
from core.facebook import Facebook


HOME_PAGE_PHRASE = 'M1 Core Service'
LOGIN_PAGE_PHRASE = 'Please sign in or register'
TASKS_PAGE_PHRASE = 'Tasks'


###   Login   ###

def attribute_error_wrapper(test_function):
    
    def inner_function(client, *args, **kwargs):
        
        with pytest.raises(AttributeError) as error:
            test_function(client, *args, **kwargs)
        assert "'NoneType' object has no attribute 'replace'" in str(error.value)
        
    return inner_function
    
    
def test_home(client):
    response = client.get('/home')
    assert HOME_PAGE_PHRASE in response.data.decode('utf-8')


def test_login(client):
    response = client.get('/login')
    assert LOGIN_PAGE_PHRASE in response.data.decode('utf-8')
    

def test_login_facebook(client):   
    facebook_response = client.post('/login', 
                                    data={'flow': 'facebook'}, 
                                    follow_redirects=True)
    assert HOME_PAGE_PHRASE in facebook_response.data.decode('utf-8')


@attribute_error_wrapper    
def test_login_code(client):
    code_response = client.get('/login?code=dummy_code')
    

@attribute_error_wrapper
def test_login_register(client):
    register_response = client.post('/login', data={'flow': 'register'})


@attribute_error_wrapper
def test_login_sign_in(client):
    sign_in_response = client.post('/login', data={'flow': 'sign-in'})


@attribute_error_wrapper
def test_logout(client):
    sign_in_response = client.get('/logout')
  

###   Algorithms   ###

def test_get_algorithms(client):
    
    response = client.get('/algorithms')
    assert b'Algorithms' in response.data
    
    response = client.get('/algorithms?type=classical')
    assert b'Extended Euclidean' in response.data
    assert b'Bernstein Vazirani' not in response.data

    response = client.get('/algorithms?type=quantum')
    assert b'Extended Euclidean' not in response.data
    assert b'Bernstein Vazirani' in response.data
    
    response = client.get('/algorithms?test_filter_name=test_filter_value')
    assert b'Algorithms' in response.data
    
    
def test_get_algorithm(client):
    response = client.get('/algorithms/egcd')
    assert b'Extended Euclidean' in response.data
    
    
@attribute_error_wrapper
def test_like_algorithm(client):
    client.get('/algorithms/egcd/like')


@attribute_error_wrapper
def test_run_algorithm(client):
    response = client.post('/algorithms/egcd/run')


def test_set_algorithm_state_enabled(client):
    client.get('/algorithms/egcd/state?enabled=True')
    
    
def test_set_algorithm_state_disabled(client):
    client.get('/algorithms/egcd/state?enabled=False')
    
    
###   Tasks   ###

def test_get_tasks(client):
    
    tasks_response = client.get('/tasks')
    task_response = client.get('/tasks?task_id=1')
    
    assert TASKS_PAGE_PHRASE in tasks_response.data.decode('utf-8') 
    assert TASKS_PAGE_PHRASE in task_response.data.decode('utf-8')
    
    

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
    

@pytest.fixture(autouse=True)
def create_mocks(client, monkeypatch):
    
    def get_home_url(*args, **kwargs):
        return '/home'

    def get_test_user_data(*args, **kwargs):
        
        test_user_data = {
            'name': 'test_name',
            'email': 'test_email',
            'full_name': 'test_full_name',
            'picture_url': 'test_picture_url',
        }
        
        return test_user_data
        
    def get_dummy_tasks(*args, **kwargs):
        
        dummy_tasks = {1:{
                'logs': ['',], 
                'run_values': {'test_run_value': '1', 'run_mode': 'classical'}, 
                'task_status': 'Done', 
                'task_id': 1, 
                'algorithm_id': 'test_algorithm', 
                'task_result': {'Result': {'test_result': 1,}}}
        }
        
        return dummy_tasks
        
    monkeypatch.setattr(Facebook, "get_autorization_url", get_home_url)
    monkeypatch.setattr(Facebook, "get_token_from_code", get_home_url)
    monkeypatch.setattr(Facebook, "get_user_data", get_test_user_data)
    
    monkeypatch.setattr(Cognito, "populate_facebook_user", get_home_url)
    
    monkeypatch.setattr(Dynamo, "like_algorithm", get_home_url)
    monkeypatch.setattr(Dynamo, "set_algorithm_state", get_home_url)
    monkeypatch.setattr(Dynamo, "get_all_tasks", get_dummy_tasks)
    
    monkeypatch.setattr(Runner, "run_algorithm", get_home_url)
    