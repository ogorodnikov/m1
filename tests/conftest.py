import pytest

from core import config


@pytest.fixture(scope="session", autouse=True)
def run_config():

    configuration = config.Config()
    
    yield configuration