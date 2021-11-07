import pytest

from core import config as core_config


@pytest.fixture(scope="session", autouse=True)
def run_config():
    configuration = core_config.Config()
    

@pytest.fixture(scope="session")
def stub():
    return lambda *args, **kwargs: None


@pytest.fixture(scope="session")    
def warn():

    def raise_user_warning(*args, **kwargs):
        raise UserWarning
    
    return raise_user_warning
    
    # return lambda *_, **__: (_ for _ in ()).throw(UserWarning)
    

def pytest_configure(config):

    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
