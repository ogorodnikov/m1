import pytest

from core.cognito import Cognito


###   General   ###

def test_get_user_pool_id(cognito_with_init):
    cognito_with_init.get_user_pool_id()

def test_get_client_id(cognito_with_init):
    cognito_with_init.get_client_id()


# ###   Login   ###

def test_login_user(cognito, test_user_form):
    cognito.login_user(test_user_form)
    

###   Register   ###
    
def test_register_user(cognito, test_user_form):
    cognito.register_user(test_user_form)

def test_disable_user(cognito, test_user_form):    
    cognito.disable_user(test_user_form)

def test_delete_user(cognito, test_user_form):
    cognito.delete_user(test_user_form)


###   Facebook   ###

def test_populate_facebook_user(cognito, test_facebook_user_data):
    cognito.populate_facebook_user(test_facebook_user_data)

def test_populate_facebook_already_in_cognito(cognito, monkeypatch, warn, test_facebook_user_data):
    
    monkeypatch.setattr("core.cognito.boto3.client.list_users",
                        lambda *_, **__: {'Users': [{'username': 'test_username'}]})
    
    cognito.populate_facebook_user(test_facebook_user_data)
    
    
###   Fixtures   ###

@pytest.fixture(scope="module", autouse=True)
def set_mocks(monkeypatch_module, stub):

    monkeypatch_module.setenv("USER_POOL", "test_user_pool")
    monkeypatch_module.setenv("USER_POOL_CLIENT", "test_client")
    
    class MockClient:
        
        __init__ = stub
        
        sign_up = stub
        admin_confirm_sign_up = stub
        admin_disable_user = stub
        admin_delete_user = stub
        
        def list_user_pools(*args, **kwargs):
            return {'UserPools': [{'Id': 'test_user_pool_id', 
                                   'Name': 'test_user_pool'}]}
                                   
        def list_user_pool_clients(*args, **kwargs):
            return {'UserPoolClients': [{'ClientId': 'test_client_id', 
                                         'ClientName': 'test_client'}]}    
        
        def initiate_auth(*args, **kwargs):
            return {'AuthenticationResult': {'AccessToken': 'test_token',
                                             'RefreshToken': 'test_token'}}
                                             
        def get_user(*args, **kwargs):
            return {'Username': 'test_username', 
                    'UserAttributes': [{'Name': 'sub',
                                        'Value': 'test_value'}]}
                                        
        def list_users(*args, **kwargs):
            return {'Users': []}
                                       
    monkeypatch_module.setattr("core.cognito.boto3.client", MockClient)
    

@pytest.fixture
def cognito(monkeypatch, stub):
    
    monkeypatch.setattr(Cognito, "get_user_pool_id", stub)
    monkeypatch.setattr(Cognito, "get_client_id", stub)
    
    return Cognito()


@pytest.fixture
def cognito_with_init(monkeypatch, stub):
    
    return Cognito()
    

@pytest.fixture
def test_user_form(cognito):
    
    return {'username': 'test_username_555', 
            'password': 'test_password_555'}


@pytest.fixture
def test_facebook_user_data(cognito, test_user_form):
    
    name = test_user_form.get('username')
    email = f"{name}@test.com"
    full_name = f"{name} {name}"
    picture_url = "https://test.com/test_picture.png"
    
    test_facebook_user_data = {
        'name': name,
        'email': email,
        'full_name': full_name,
        'picture_url': picture_url
    }
    
    fb_username = 'fb_' + email.replace('@', '_')
    
    return test_facebook_user_data