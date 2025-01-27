import pytest

from decimal import Decimal

from contextlib import contextmanager

from core.dynamo import Dynamo


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


no_service_record_response = {}
no_queued_tasks_response = {'Attributes': {'queued_tasks': []}}
queued_tasks_response = {'Attributes': {'queued_tasks': [1, 2, 3]}}

@pytest.mark.parametrize("update_response", [no_service_record_response,
                                             no_queued_tasks_response,
                                             queued_tasks_response])
def test_get_next_task(db, monkeypatch, update_response):
    
    def mock_update_item(*args, **kwargs):
        return update_response
    
    monkeypatch.setattr(MockTable, "update_item", mock_update_item)

    db.get_next_task()


@pytest.mark.parametrize("append", [True, False])
def test_update_task_attribute(db, append):
    
    db.update_task_attribute(
        task_id=1, 
        attribute='test_attribute', 
        value='test_value', 
        append=append
    )
    

def test_purge_tasks(db, monkeypatch):
    
    def mock_scan(*args, **kwargs):
        
        if not kwargs.get('ExclusiveStartKey'):
            return {'Items': ['test_item_1'], 'LastEvaluatedKey': 'test_key'}
        
        else:
            return {'Items': ['test_item_2']}    
    
    monkeypatch.setattr(MockTable, "scan", mock_scan)

    db.purge_tasks()


###   Statuses   ###
    
def test_add_status_update(db, monkeypatch, stub):
    
    monkeypatch.setattr(Dynamo, "update_task_attribute", stub)
    
    db.add_status_update(task_id=1, status='test_status', result='test_result')
        

def test_get_status_updates(db, monkeypatch):
    
    test_response = {'Attributes': {'status_updates': []}}
    
    monkeypatch.setattr(MockTable, "update_item", lambda *_, **__: test_response)
    
    db.get_status_updates()
    
    
def test_get_status_updates_empty(db, monkeypatch):
    
    monkeypatch.setattr(MockTable, "update_item", lambda *_, **__: {})
    
    db.get_status_updates()


def test_replace_status_updates(db):
    
    status_updates = [[Decimal('86'), 'Running', ''], 
                      [Decimal('86'), 'Done', {'Result': {'GCD': Decimal('3'), 
                                               'Bézout coefficients': 
                                                   [Decimal('-51462392'), 
                                                    Decimal('39.5')]}}]]
                                                    
    replaced_status_updates = [[86, 'Running', ''], 
                               [86, 'Done', {'Result': {'GCD': 3, 
                                             'Bézout coefficients':
                                                [-51462392, 39.5]}}]]
                                                
    assert db.replace_decimals(status_updates) == replaced_status_updates
    

###   S3  ###

def test_move_figure_to_s3(db, monkeypatch, stub):
    monkeypatch.setattr("core.dynamo.os.remove", stub)
    db.move_figure_to_s3(from_path='', to_path='')

def test_stream_figure_from_s3(db):
    db.stream_figure_from_s3(s3_from_path='')

def test_purge_s3_folder(db):
    db.purge_s3_folder(prefix='test_prefix')


###   Test Data   ##
    
def test_add_test_data(db):
    db.add_test_data()

        
###   Fixtures   ###

class MockBatch:
    
    def delete_item(*args, **kwargs):
        pass
    
    def put_item(*args, **kwargs):
        pass
    

class MockTable:
            
    def __init__(*args, **kwargs):
        pass
    
    def update_item(*args, **kwargs):
        return {'ResponseMetadata': {'HTTPStatusCode': 200},
                'Attributes': {}}
    
    def scan(*args, **kwargs):
        return {'Items': []}
        
    def query(*args, **kwargs):
        return {'Items': [{'task_id': 0, 'task': []}]}
        
    def get_item(*args, **kwargs):
        return {'Item': []}
      
    @contextmanager 
    def batch_writer(*args, **kwargs):

        yield MockBatch


class MockBucket:
    
    def __init__(*args, **kwargs):
        pass
    
    def upload_file(*args, **kwargs):
        pass
    
    def download_fileobj(*args, **kwargs):
        pass
    
    class MockObjects:
        
        def filter(*args, **kwargs):
            
            return type("MockFilter", (), {'delete': lambda: None})
            
    objects = MockObjects
    
            
class MockDynamoResource:
        
    def __init__(*args, **kwargs):
        pass
    
    Table = MockTable
    Bucket = MockBucket
            

@pytest.fixture(scope="module")
def db():
    return Dynamo()


@pytest.fixture(scope="module", autouse=True)
def set_mocks(mock):
    
    mock("core.dynamo.resource", MockDynamoResource)