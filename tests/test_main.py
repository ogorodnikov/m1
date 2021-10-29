import pytest

from _pytest.monkeypatch import MonkeyPatch

from core.main import Main

from core.app import FlaskApp
from core.app import create_app

from core.dynamo import Dynamo
from core.runner import Runner
from core.routes import Routes
from core.cognito import Cognito
from core.telegram import Bot
from core.facebook import Facebook


def test_start_logging(test_main):
    
    # test_main = Main()
    test_main.start_logging()



# def test_logging(users, caplog):
    
#     message = "Test log :)"
#     users.log(message)
#     print('Print test')
    
#     logging.getLogger('users').info("log test!")
    
#     print(f"caplog.text {caplog.text}")
    
#     print(f"caplog.records {caplog.records}")
    
#     print(f"caplog.get_records('setup') {caplog.get_records('setup')}")
#     print(f"caplog.get_records('call') {caplog.get_records('call')}")
#     print(f"caplog.get_records('teardown') {caplog.get_records('teardown')}")
    
    
    
    # raise 

    # assert message in capture_output["stderr"]    

# def test_log(users, capture_output):
    
#     message = "Test log :)"
#     users.log(message)
#     assert message in capture_output["stderr"]


# def test_log_to_file():
    
#     with NamedTemporaryFile() as temporary_file:
        
#         configuration = config.Config(log_file_path=temporary_file.name)
        
#         logs = temporary_file.read().decode("utf-8")
        
#         assert "LOGGING initiated" in logs


# def test_print_environ(run_config):
#     run_config.print_environ()



###   Fixtures   ###


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
    
    
@pytest.fixture(scope="module")
def test_main():
    
    test_main = Main()

    yield test_main
    
    # test_main.runner.stop()




# @pytest.fixture
# def capture_output(monkeypatch):
    
#     buffer = {"stderr": ""}

#     def capture(message):
#         buffer["stderr"] += message

#     monkeypatch.setattr(sys.stderr, 'write', capture)

#     return buffer



