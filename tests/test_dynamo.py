import pytest

from _pytest.monkeypatch import MonkeyPatch

from core.dynamo import Dynamo

import boto3


###   Algorithms   ###

def test_get_all_algorithms(db):
    db.get_all_algorithms()
    
    
def test_query_algorithms(db):
    db.query_algorithms(query_parameters={'test_filter': 'test_value'})


def test_get_algorithm(db):
    db.get_algorithm(algorithm_id='test_algorithm')
    
  
def test_like_algorithm(db):
    db.like_algorithm(algorithm_id='test_algorithm')


@pytest.mark.parametrize("is_enabled", [True, False])
def test_set_algorithm_state(db, is_enabled):
    db.set_algorithm_state(algorithm_id='test_algorithm', is_enabled=is_enabled)


###   Tasks   ###

def test_get_all_tasks(db):
    db.get_all_tasks()
    
    
def test_add_task(db):
    db.add_task(algorithm_id='test_algorithm', run_values='test_run_values')


def test_get_next_task_no_service_record(db, monkeypatch):
    
    # def raise_warning(*args, **kwargs):
    #     raise UserWarning
        
    no_service_record_response = {}
    
    monkeypatch.setattr(MockTable, "update_response", no_service_record_response)

    db.get_next_task()


def test_get_next_task_no_queued_tasks(db, monkeypatch):
    
    no_queued_tasks_response = {'Attributes': {'queued_tasks': []}}
    
    monkeypatch.setattr(MockTable, "update_response", no_queued_tasks_response)

    db.get_next_task()
    





###   Fixtures   ###


class MockTable:
            
    update_response = {'ResponseMetadata': {'HTTPStatusCode': 200},
                       'Attributes': {}}
            
    def __init__(*args, **kwargs):
        pass
    
    def update_item(*args, **kwargs):
        return __class__.update_response
    
    def scan(*args, **kwargs):
        return {'Items': []}
        
    def query(*args, **kwargs):
        return {'Items': [{'task_id': 0, 'task': []}]}
        
    def get_item(*args, **kwargs):
        return {'Item': []}
        

class MockBucket:
            
    def __init__(*args, **kwargs):
        pass
    
            
class MockDynamoResource:
        
    def __init__(*args, **kwargs):
        pass
    
    Table = MockTable
    Bucket = MockBucket
        
            

@pytest.fixture(scope="module")
def db():

    db = Dynamo()    

    yield db
    
    
@pytest.fixture(scope="module")
def monkeypatch_module():
    
    monkeypatch_module = MonkeyPatch()
    yield monkeypatch_module
    monkeypatch_module.undo()


@pytest.fixture(autouse=True, scope="module")
def mocks(monkeypatch_module):
    
    monkeypatch_module.setattr("core.dynamo.resource", MockDynamoResource)
    
    # monkeypatch_module.setattr(Dynamo, "algorithms", MockTable())