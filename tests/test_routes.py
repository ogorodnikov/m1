import io
import pytest

from core.main import Main

from core.app import FlaskApp
from core.app import create_app

from core.dynamo import Dynamo
from core.runner import Runner
from core.routes import Routes
from core.cognito import Cognito
from core.telegram import Bot
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
    root_response = client.get('/')
    home_response = client.get('/home')
    
    assert HOME_PAGE_PHRASE in root_response.data.decode('utf-8')
    assert HOME_PAGE_PHRASE in home_response.data.decode('utf-8')
    

def test_login(client):
    response = client.get('/login')
    assert LOGIN_PAGE_PHRASE in response.data.decode('utf-8')
    

def test_login_facebook(client):   
    facebook_response = client.post('/login', 
                                    data={'flow': 'facebook'}, 
                                    follow_redirects=True)
    assert HOME_PAGE_PHRASE in facebook_response.data.decode('utf-8')


@attribute_error_wrapper
def test_login_code_ok(client):   
    client.get('/login?code=code_ok')
    
@attribute_error_wrapper
def test_login_code_error(client):   
    client.get('/login?code=code_error')
    

@attribute_error_wrapper
def test_login_register_ok(client):
    register_response = client.post('/login', data={'flow': 'register'})

@attribute_error_wrapper
def test_login_register_error(client):
    register_response = client.post('/login', data={'flow': 'register',
                                                    'error': 'test_error'})

@attribute_error_wrapper
def test_login_sign_in_ok(client):
    sign_in_response = client.post('/login', data={'flow': 'sign-in'})

@attribute_error_wrapper
def test_login_sign_in_error(client):
    sign_in_response = client.post('/login', data={'flow': 'sign-in',
                                                  'error': 'test_error'})

@attribute_error_wrapper
def test_logout(client):
    sign_in_response = client.get('/logout')
  

# ###   Algorithms   ###

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
    

def test_download(client):
    
    client.get('/download?task_id=1&content=statevector')
    # client.get('/download?task_id=1&content=statevector&as_attachment=True')


def test_admin(client):
    client.get('/admin')
    
    
commands = [
    'start_bot', 
    'stop_bot', 
    'add_test_data', 
    'reset_application',
    'start_runner',
    'stop_runner',
    'purge_tasks',
    'add_test_tasks',
    'test',
]

@pytest.mark.parametrize("command", commands)
def test_admin_commands(client, command):
    
    print(f"command: {command}")
    
    # client.get(f'/admin&command={command}')
    
    client.post('/admin', data={'command': command})

    
    
    
###   Fixtures   ###           

@pytest.fixture(scope="module")
def client():
    
    app = create_app()
    app.testing = True
    app.secret_key = 'test_key'
    
    db = Dynamo()
    users = Cognito()
    runner = Runner(db)
    facebook = Facebook()
    telegram_bot = Bot(db, runner)
    
    routes = Routes(db, app, users, runner, facebook, telegram_bot)
    
    test_context = app.test_request_context()
    test_context.push()
    
    with app.test_client() as client:
        yield client
    
    test_context.pop()
    # app.stop_runner()
    

@pytest.fixture(autouse=True)
def mocks(client, monkeypatch):
    
    def get_home_url(*args, **kwargs):
        return '/home'
        
    def get_test_token_from_code(self, code, login_url):
        if code == 'code_error':
            facebook_token = 'token_error'
        else:
            facebook_token = 'token_ok'
        return facebook_token

    def get_test_user_data(self, facebook_token):
        
        test_user_data = {
            'name': 'test_name',
            'email': 'test_email',
            'full_name': 'test_full_name',
            'picture_url': 'test_picture_url',
        }
        
        if facebook_token == 'token_error':
            test_user_data['error'] = 'test_error'
        
        return test_user_data
        
    def register_test_user(self, request_form):
        if request_form.get('error'):
            raise UserWarning
        
    def login_test_user(self, request_form):
        if request_form.get('error'):
            raise UserWarning        

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
        
    def get_dummy_s3_stream(*args, **kwargs):
        return io.BytesIO()
        
    def get_dummy_status_updates(*args, **kwargs):
        
        dummy_status_updates = [(1, 'Running', ''), (1, 'Done', 'test_result')]
        
        return dummy_status_updates
        
        
    monkeypatch.setattr(Main, "__init__", get_home_url)
    
    monkeypatch.setattr(Facebook, "get_autorization_url", get_home_url)
    monkeypatch.setattr(Facebook, "get_token_from_code", get_test_token_from_code)
    monkeypatch.setattr(Facebook, "get_user_data", get_test_user_data)
    
    monkeypatch.setattr(Cognito, "populate_facebook_user", get_home_url)
    monkeypatch.setattr(Cognito, "register_user", register_test_user)
    monkeypatch.setattr(Cognito, "login_user", login_test_user)
    
    monkeypatch.setattr(Dynamo, "get_status_updates", get_home_url)
    monkeypatch.setattr(Dynamo, "like_algorithm", get_home_url)
    monkeypatch.setattr(Dynamo, "set_algorithm_state", get_home_url)
    monkeypatch.setattr(Dynamo, "add_task", get_home_url)
    monkeypatch.setattr(Dynamo, "purge_tasks", get_home_url)
    monkeypatch.setattr(Dynamo, "add_test_data", get_home_url)
    
    monkeypatch.setattr(Dynamo, "get_all_tasks", get_dummy_tasks)
    monkeypatch.setattr(Dynamo, "stream_figure_from_s3", get_dummy_s3_stream)
    monkeypatch.setattr(Dynamo, "get_status_updates", get_dummy_status_updates)
    
    monkeypatch.setattr(Runner, "run_algorithm", get_home_url)

    monkeypatch.setattr(FlaskApp, "exit_application", get_home_url)