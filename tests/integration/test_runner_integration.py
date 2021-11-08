import pytest

from qiskit import QuantumCircuit

from core.runner import Runner
from core.dynamo import Dynamo

from test_runner import set_mocks
from test_runner import runner
from test_runner import test_task
from test_runner import get_test_task


def test_execute_task(runner, monkeypatch, stub):
    
    monkeypatch.setattr(Runner, "monitor_job", stub)
    
    test_circuit = QuantumCircuit()
    test_backend = runner.simulator_backend
    
    runner.execute_task(task_id=None, circuit=test_circuit, backend=test_backend)
    
    
###   Fixtures   ###

@pytest.fixture(scope="module", autouse=True)
def set_mocks(mock, get_test_task, stub):
    
    mock(Dynamo, "__init__", stub)
    mock(Dynamo, "add_task", stub)
    mock(Dynamo, "add_status_update", stub)
    mock(Dynamo, "update_task_attribute", stub)
    mock(Dynamo, "move_figure_to_s3", stub)
    
    mock(Dynamo, "get_next_task", get_test_task)
    

@pytest.fixture
def runner():
    return Runner(db=Dynamo())