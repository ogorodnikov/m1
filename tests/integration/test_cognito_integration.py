import pytest

from core.cognito import Cognito


###   General   ###

def test_get_user_pool_id(cognito):
    
    user_pool = cognito.user_pool
    user_pool_id = cognito.get_user_pool_id(user_pool)
    
    # assert user_pool_id == "us-east-1_HhJBks0a8"
    assert len(user_pool_id) == 19
    

def test_get_client_id(cognito):
    
    user_pool_id = cognito.user_pool_id
    user_pool_client = cognito.user_pool_client
    client_id = cognito.get_client_id(user_pool_id, user_pool_client)

    # assert client_id == "1fhh6jkt6c8ji76vk9i04u5d9f"
    assert len(client_id) == 26


###   Login   ###

@pytest.mark.parametrize("remember_me", ['True', 'False'])
def test_login_user_pass(cognito, test_user, remember_me):
    
    test_user.update({'remember_me': remember_me})
    
    cognito.login_user(test_user)
    
    
def test_login_user_exception(cognito, test_user_form):
    
    login_form = test_user_form.update((
        ('remember_me', 'True'), 
        ('flow', 'sign-in')
    ))
    
    with pytest.raises(Exception) as exception:
    
        cognito.login_user(test_user_form)
    
    assert "UserNotFoundException" in str(exception.value)
    

###   Register   ###
    
def test_register_disable_delete_user(cognito, test_user_form):
    
    cognito.register_user(test_user_form)
    cognito.disable_user(test_user_form)
    cognito.delete_user(test_user_form)
    

def test_duplicate_register_user_exception(cognito, test_user):
    
    with pytest.raises(Exception) as exception:

        cognito.register_user(test_user)
    
    assert "UsernameExistsException" in str(exception.value)
    

def test_populate_facebook_user(cognito, test_facebook_user_data):
    
    cognito.populate_facebook_user(test_facebook_user_data)


def test_populate_facebook_user_duplicated(cognito, test_facebook_user_data):
    
    cognito.populate_facebook_user(test_facebook_user_data)
    cognito.populate_facebook_user(test_facebook_user_data)
    
    
###   Fixtures   ###

@pytest.fixture(scope="module")
def cognito():
    return Cognito()
    

@pytest.fixture
def test_user_form(cognito):
    
    return {'username': 'test_username_555', 
            'password': 'test_password_555'}

    
@pytest.fixture
def test_user(cognito, test_user_form):
    
    cognito.register_user(test_user_form)
    
    yield test_user_form
    
    cognito.delete_user(test_user_form)


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
    
    yield test_facebook_user_data
    
    cognito.delete_user({'username': fb_username})