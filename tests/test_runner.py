import os
import pytest

from core.runner import Runner
from core.dynamo import Dynamo


def test_runner_state(test_runner):
    assert os.environ.get('RUNNER_STATE') == 'Running'

@pytest.fixture(scope="session")
def test_runner():

    db = Dynamo()    
    test_runner = Runner(db)
    test_runner.start()
    
    yield test_runner
    
    test_runner.stop()

