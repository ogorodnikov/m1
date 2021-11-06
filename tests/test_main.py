import pytest
import logging

from _pytest.monkeypatch import MonkeyPatch

from core.main import Main

from core.app import FlaskApp
from core.config import Config
from core.routes import Routes
from core.dynamo import Dynamo
from core.runner import Runner
from core.cognito import Cognito
from core.telegram import Bot
from core.facebook import Facebook


###   Logging   ###

def test_start_logging(main, tmpdir):
    main.start_logging(log_to_file=True, log_file_path=tmpdir)
    
    
def test_logging(main, caplog):

    test_message = 'Logging test'
    
    caplog.set_level(logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.info(test_message)
    
    assert caplog.record_tuples == [("root", logging.INFO, test_message)]


###   Fixtures   ###

@pytest.fixture(scope="module")
def main():
    return Main()


@pytest.fixture(scope="module")
def monkeypatch_module(request):
    
    monkeypatch_module = MonkeyPatch()
    yield monkeypatch_module
    monkeypatch_module.undo()
    

@pytest.fixture(autouse=True, scope="module")
def mocks(monkeypatch_module, stub):
    
    def test(*args, **kwargs):
        raise UserWarning
    
    
    class MockFlaskApp:
        
        class MockConfig:
            
            def from_object(config):
                pass
        
        config = MockConfig
    
    
    from flask import Config as C
    from flask import Flask
    
    monkeypatch_module.setattr(Bot, "start", stub)
    monkeypatch_module.setattr(Runner, "start", stub)
    monkeypatch_module.setattr(C, "from_object", stub)
    
    monkeypatch_module.setattr(FlaskApp, "__init__", Flask.__init__)
    monkeypatch_module.setattr(Config, "__init__", stub) 
    monkeypatch_module.setattr(Routes, "__init__", stub) 
    monkeypatch_module.setattr(Dynamo, "__init__", stub) 
    monkeypatch_module.setattr(Runner, "__init__", stub) 
    monkeypatch_module.setattr(Cognito, "__init__", stub) 
    monkeypatch_module.setattr(Bot, "__init__", stub) 
    monkeypatch_module.setattr(Facebook, "__init__", stub)