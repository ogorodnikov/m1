import pytest

from urllib.parse import urlencode

from core import facebook


# General tests

def test_get_autorization_url(fb):
    
    dummy_login_url = "https://m1.ogoro.me/login"
    dummy_scope = "public_profile,email"
    
    dummy_url_parameters = urlencode({'redirect_uri': dummy_login_url,
                                      'scope': dummy_scope})
    
    autorization_url = fb.get_autorization_url(dummy_login_url)
    
    assert dummy_url_parameters in autorization_url
    

def test_get_token_from_code_none(fb):
    
    dummy_login_url = "https://m1.ogoro.me/login"
    dummy_code = "K3QdgthmpEUoxpfocnmOs7OVGFO4X"
    
    facebook_token = fb.get_token_from_code(dummy_code, dummy_login_url)
    
    assert facebook_token is None
    
    
def test_get_user_data(fb):
    
    dummy_access_token = "K3QdgthmpEUoxpfocnmOs7OVGFO4X"
    
    user_data = fb.get_user_data(dummy_access_token)
    
    assert not any(user_data)

    
###   Fixtures

@pytest.fixture(scope="module")
def fb():
    
    fb = facebook.FB()
    
    yield fb