import pytest

from core import config as core_config


@pytest.fixture(scope="session", autouse=True)
def run_config():

    configuration = core_config.Config()
    
    yield configuration
    

def pytest_configure(config):

    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
