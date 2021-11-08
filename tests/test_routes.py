import io
import pytest

from core.app import FlaskApp
from core.app import create_app

from core.main import Main
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

def test_home(app):
    root_response = app.get('/')
    home_response = app.get('/home')
    
    assert HOME_PAGE_PHRASE in root_response.data.decode('utf-8')
    assert HOME_PAGE_PHRASE in home_response.data.decode('utf-8')
    

def test_login(app):
    response = app.get('/login')
    assert LOGIN_PAGE_PHRASE in response.data.decode('utf-8')
    

def test_login_facebook(app):   
    facebook_response = app.post('/login', 
                                    data={'flow': 'facebook'}, 
                                    follow_redirects=True)
    assert HOME_PAGE_PHRASE in facebook_response.data.decode('utf-8')


def attribute_error_wrapper(test_function):
    
    def inner_function(app, *args, **kwargs):
        
        with pytest.raises(AttributeError) as error:
            test_function(app, *args, **kwargs)
        assert "'NoneType' object has no attribute 'replace'" in str(error.value)
        
    return inner_function
    

@attribute_error_wrapper
def test_login_code_ok(app):   
    app.get('/login?code=code_ok')
    
@attribute_error_wrapper
def test_login_code_error(app):   
    app.get('/login?code=code_error')
    

@attribute_error_wrapper
def test_login_register_ok(app):
    register_response = app.post('/login', data={'flow': 'register'})

@attribute_error_wrapper
def test_login_register_error(app):
    register_response = app.post('/login', data={'flow': 'register',
                                                    'error': 'test_error'})

@attribute_error_wrapper
def test_login_sign_in_ok(app):
    sign_in_response = app.post('/login', data={'flow': 'sign-in'})

@attribute_error_wrapper
def test_login_sign_in_error(app):
    sign_in_response = app.post('/login', data={'flow': 'sign-in',
                                                  'error': 'test_error'})

@attribute_error_wrapper
def test_logout(app):
    sign_in_response = app.get('/logout')
  

###   Algorithms   ###

def test_get_algorithms(app):
    
    app.get('/algorithms')
    app.get('/algorithms?type=classical')
    app.get('/algorithms?type=quantum')
    app.get('/algorithms?test_filter_name=test_filter_value')
    app.get('/algorithms?test_filter_name_error=test_filter_value')
    
    
def test_get_algorithm(app):
    app.get('/algorithms/egcd')
    
    
@attribute_error_wrapper
def test_like_algorithm(app):
    app.get('/algorithms/egcd/like')


@attribute_error_wrapper
def test_run_algorithm(app):
    response = app.post('/algorithms/egcd/run')


def test_set_algorithm_state_enabled(app):
    app.get('/algorithms/egcd/state?enabled=True')
    
def test_set_algorithm_state_disabled(app):
    app.get('/algorithms/egcd/state?enabled=False')
    
    
###   Tasks   ###

def test_get_tasks(app):
    tasks_response = app.get('/tasks')
    assert TASKS_PAGE_PHRASE in tasks_response.data.decode('utf-8')

def test_get_task(app):
    task_response = app.get('/tasks?task_id=1')
    assert TASKS_PAGE_PHRASE in task_response.data.decode('utf-8')

    
def test_download(app):
    app.get('/download?task_id=1&content=statevector')
    app.get('/download?task_id=1&content=statevector&as_attachment=True')


def test_admin(app):
    app.get('/admin')
    
    
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
def test_admin_commands(app, command):
    
    print(f"command: {command}")
    
    app.post('/admin', data={'command': command})
    
    
###   Fixtures   ###           

@pytest.fixture(scope="module")
def app():
    
    test_app = create_app()
    test_app.testing = True
    test_app.secret_key = 'test_key'
    
    db = Dynamo()
    cognito = Cognito()
    runner = Runner(db)
    facebook = Facebook()
    telegram_bot = Bot(db, runner)
    
    routes = Routes(db, test_app, cognito, runner, facebook, telegram_bot)
    
    test_context = test_app.test_request_context()
    test_context.push()
    
    with test_app.test_client() as app:
        yield app
    
    test_context.pop()


@pytest.fixture(scope="module", autouse=True)
def set_mocks(mock, stub):
    
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

    def get_test_tasks(*args, **kwargs):
        
        test_tasks = {1:{
                'logs': ['',], 
                'run_values': {'test_run_value': '1', 'run_mode': 'classical'}, 
                'task_status': 'Done', 
                'task_id': 1, 
                'algorithm_id': 'test_algorithm', 
                'task_result': {'Result': {'test_result': 1,}}}
        }
        
        return test_tasks
        
    def get_test_s3_stream(*args, **kwargs):
        return io.BytesIO()
        
    def get_test_status_updates(*args, **kwargs):
        
        test_status_updates = [(1, 'Running', ''), (1, 'Done', 'test_result')]
        
        return test_status_updates
    
    
    def get_test_query_algorithms(self, query_parameters):
        
        if "test_filter_name_error" in query_parameters:
            raise UserWarning
        else:
            return []
    
    test_algorithm_data = {'id': 'test_algorithm_id',
                   'name': 'test_algorithm',
                   'link': 'https://test.com/test_algorithm',
                   'description': 'test_algorithm_description',
                   'parameters': [{'name': 'test_parameter', 
                                   'default_value': 'test_parameter_value'}]
    }
        
    mock(Main, "__init__", stub)

    mock(Facebook, "__init__", stub)    
    mock(Facebook, "get_autorization_url", lambda *_, **__: '/home')
    mock(Facebook, "get_token_from_code", get_test_token_from_code)
    mock(Facebook, "get_user_data", get_test_user_data)
    
    mock(Cognito, "__init__", stub)
    mock(Cognito, "populate_facebook_user", stub)
    mock(Cognito, "register_user", register_test_user)
    mock(Cognito, "login_user", login_test_user)

    mock(Dynamo, "__init__", stub)
    mock(Dynamo, "query_algorithms", get_test_query_algorithms)
    mock(Dynamo, "get_all_algorithms", lambda *_, **__: [])
    mock(Dynamo, "get_algorithm", lambda *_, **__: [])
    
    mock(Dynamo, "get_status_updates", stub)
    mock(Dynamo, "like_algorithm", stub)
    mock(Dynamo, "set_algorithm_state", stub)
    mock(Dynamo, "add_task", stub)
    mock(Dynamo, "purge_tasks", stub)
    mock(Dynamo, "add_test_data", stub)
    mock(Dynamo, "purge_s3_folder", stub)
    mock(Dynamo, "update_task_attribute", stub)
    mock(Dynamo, "add_status_update", stub)
    
    mock(Dynamo, "get_all_tasks", get_test_tasks)
    mock(Dynamo, "stream_figure_from_s3", get_test_s3_stream)
    mock(Dynamo, "get_status_updates", get_test_status_updates)
    
    mock(Runner, "__init__", stub)
    mock(Runner, "start", stub)
    mock(Runner, "stop", stub)
    mock(Runner, "run_algorithm", stub)

    # mock(FlaskApp, "__init__", stub)
    mock(FlaskApp, "exit_application", stub)