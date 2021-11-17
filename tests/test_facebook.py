import pytest

from urllib.parse import urlencode

from core.facebook import Facebook


###   Facebook   ###

def test_get_autorization_url(fb):
    
    test_login_url = "https://test.com/login"
    test_scope = "public_profile,email"
    
    test_url_parameters = urlencode({'redirect_uri': test_login_url,
                                      'scope': test_scope})
    
    autorization_url = fb.get_autorization_url(test_login_url)
    
    assert test_url_parameters in autorization_url
    

def test_get_token_from_code_none(fb):
    
    test_login_url = "https://test.com/login"
    test_code = "K3QdgthmpEUoxpfocnmOs7OVGFO4X"
    
    facebook_token = fb.get_token_from_code(test_code, test_login_url)
    
    assert facebook_token is None
    
    
def test_get_user_data_error(fb):
    
    test_access_token = "K3QdgthmpEUoxpfocnmOs7OVGFO4X"
    user_data = fb.get_user_data(test_access_token)

    assert "Invalid OAuth access token" in user_data['error']['message']

    
###   Fixtures   ###

@pytest.fixture(scope="module")
def fb():
    return Facebook()


@pytest.fixture(scope="module", autouse=True)
def set_mocks(monkeypatch_module):
    
    monkeypatch_module.setenv('DOMAIN', '')
    monkeypatch_module.setenv('AWS_NLB', '')