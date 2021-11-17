import pytest

from _pytest.monkeypatch import MonkeyPatch



# from core import config as core_config

# @pytest.fixture(scope="session", autouse=True)
# def run_config():
#     configuration = core_config.Config()


@pytest.fixture(scope="session", autouse=True)
def stub():
    return lambda *args, **kwargs: None


@pytest.fixture(scope="session", autouse=True)    
def warn():
    return lambda *_, **__: (_ for _ in ()).throw(UserWarning)


@pytest.fixture(scope="module")
def monkeypatch_module():
    
    monkeypatch_module = MonkeyPatch()
    yield monkeypatch_module
    monkeypatch_module.undo()
    
    
@pytest.fixture(scope="module")
def mock(monkeypatch_module):    
    return monkeypatch_module.setattr


@pytest.fixture(scope="module")
def mock_env(monkeypatch_module):    
    return monkeypatch_module.setenv
    

def pytest_configure(config):

    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
