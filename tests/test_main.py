import pytest
import logging

from _pytest.monkeypatch import MonkeyPatch

from flask import Flask
from flask import Config as FlaskConfig    

from core.main import Main

from core.app import FlaskApp
from core.runner import Runner
from core.telegram import Bot


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
    

@pytest.fixture(scope="module", autouse=True)
def mocks(monkeypatch_module, stub):
    
    monkeypatch_module.setattr("core.main.Config", stub) 
    monkeypatch_module.setattr("core.main.Routes", stub) 
    monkeypatch_module.setattr("core.main.Dynamo", stub) 
    monkeypatch_module.setattr("core.main.Cognito", stub)
    monkeypatch_module.setattr("core.main.Facebook", stub)

    monkeypatch_module.setattr(Bot, "__init__", stub)    
    monkeypatch_module.setattr(Runner, "__init__", stub)
    
    monkeypatch_module.setattr(FlaskApp, "__init__", Flask.__init__)    
    monkeypatch_module.setattr(FlaskConfig, "from_object", stub)

    monkeypatch_module.setattr(Bot, "start", stub)
    monkeypatch_module.setattr(Runner, "start", stub)