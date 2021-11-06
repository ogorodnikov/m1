import pytest

from core import config as core_config


@pytest.fixture(scope="session", autouse=True)
def run_config():
    configuration = core_config.Config()
    

@pytest.fixture(scope="session")
def stub():
    
    def get_none(*args, **kwargs):
        pass
    
    return get_none
    

def pytest_configure(config):

    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
