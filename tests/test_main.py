import pytest
import logging

from _pytest.monkeypatch import MonkeyPatch

from core.main import Main
from core.runner import Runner
from core.telegram import Bot


###   Logging   ###

def test_start_logging(test_main, tmpdir):
    test_main.start_logging(log_to_file=True, log_file_path=tmpdir)
    
    
def test_logging(test_main, caplog):

    test_message = 'Logging test'
    
    caplog.set_level(logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.info(test_message)
    
    assert caplog.record_tuples == [("root", logging.INFO, test_message)]


###   Fixtures   ###

@pytest.fixture(scope="module")
def test_main():
    
    test_main = Main()
    yield test_main

    
@pytest.fixture(scope="module")
def monkeypatch_module(request):
    
    monkeypatch_module = MonkeyPatch()
    yield monkeypatch_module
    monkeypatch_module.undo()
    

@pytest.fixture(autouse=True, scope="module")
def mocks(monkeypatch_module):
    
    def stub(*args, **kwargs):
        pass
        
    monkeypatch_module.setattr(Bot, "start", stub)
    monkeypatch_module.setattr(Runner, "start", stub)





