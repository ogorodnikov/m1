import pytest

from _pytest.monkeypatch import MonkeyPatch

from core.dynamo import Dynamo

import boto3


###   Algorithms   ###


def test_get_all_algorithms(db):
    db.get_all_algorithms()
    

def test_query_algorithms(db):
    
    test_query_parameters = {'test_filter': 'test_value'}
    
    db.query_algorithms(test_query_parameters)
    
    

###   Fixtures   ###

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
    
    
    class MockDynamoResource:
        
        def __init__(*args, **kwargs):
            pass
    
        class Table:
                    
            def __init__(*args, **kwargs):
                pass
            
            def update_item(*args, **kwargs):
                pass
            
            def scan(*args, **kwargs):
                return {'Items': []}
                
            def query(*args, **kwargs):
                return {'Items': []}

        class Bucket:
                    
            def __init__(*args, **kwargs):
                pass
  

        
    
    monkeypatch_module.setattr("core.dynamo.resource", MockDynamoResource)
    
    # monkeypatch_module.setattr(Dynamo, "algorithms", MockTable())