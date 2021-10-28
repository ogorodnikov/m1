import pytest

from core import cognito


###   General tests   ###

def test_get_user_pool_id(users):
    
    user_pool = users.user_pool
    user_pool_id = users.get_user_pool_id(user_pool)
    
    # assert user_pool_id == "us-east-1_HhJBks0a8"
    assert len(user_pool_id) == 19
    

def test_get_client_id(users):
    
    user_pool_id = users.user_pool_id
    user_pool_client = users.user_pool_client
    client_id = users.get_client_id(user_pool_id, user_pool_client)

    # assert client_id == "1fhh6jkt6c8ji76vk9i04u5d9f"
    assert len(client_id) == 26


###   Login   ###

@pytest.mark.parametrize("remember_me", ['True', 'False'])
def test_login_user_pass(users, test_user, remember_me):
    
    test_user.update({'remember_me': remember_me})
    
    users.login_user(test_user)
    
    
def test_login_user_exception(users, test_user_form):
    
    login_form = test_user_form.update((
        ('remember_me', 'True'), 
        ('flow', 'sign-in')
    ))
    
    with pytest.raises(Exception) as exception:
    
        users.login_user(test_user_form)
    
    assert "UserNotFoundException" in str(exception.value)
    

###   Register   ###
    
def test_register_disable_delete_user(users, test_user_form):
    
    users.register_user(test_user_form)
    users.disable_user(test_user_form)
    users.delete_user(test_user_form)
    

def test_duplicate_register_user_exception(users, test_user):
    
    with pytest.raises(Exception) as exception:

        users.register_user(test_user)
    
    assert "UsernameExistsException" in str(exception.value)
    

def test_populate_facebook_user(users, test_user_data):
    
    users.populate_facebook_user(test_user_data)


def test_populate_facebook_user_duplicated(users, test_user_data):
    
    users.populate_facebook_user(test_user_data)
    users.populate_facebook_user(test_user_data)
    
    
###   Fixtures   ###

@pytest.fixture(scope="module")
def users():
    
    users = cognito.Cognito()
    
    yield users
    

@pytest.fixture
def test_user_form(users):
    
    test_username = f"test_username_555"
    test_password = f"test_password_555"
    
    test_user_form = dict((('username', test_username), ('password', test_password)))
    
    yield test_user_form
    
    
@pytest.fixture
def test_user(users, test_user_form):
    
    users.register_user(test_user_form)
    
    yield test_user_form
    
    users.delete_user(test_user_form)


@pytest.fixture
def test_user_data(users, test_user_form):
    
    name = test_user_form.get('username')
    email = f"{name}@test.com"
    full_name = f"{name} {name}"
    picture_url = "https://test.com/test_picture.png"
    
    test_user_data = {
        'name': name,
        'email': email,
        'full_name': full_name,
        'picture_url': picture_url
    }
    
    fb_username = 'fb_' + email.replace('@', '_')
    
    yield test_user_data
    
    users.delete_user({'username': fb_username})