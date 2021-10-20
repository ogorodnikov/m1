# import pytest

# from core import engine



# def test_runner(test_app):
    

#     runner = test_app.config['RUNNER']
    
#     print(f"runner {runner}")
    
#     assert test_app.config['RUNNER_STATE'] == 'Started'
    
#     runner.stop()
    
#     assert test_app.config['RUNNER_STATE'] == 'Stopped'
    
#     runner.start()    
    
#     assert test_app.config['RUNNER_STATE'] == 'Started'

    



# @pytest.fixture(scope="session")
# def test_app():
    
#     from core.app import app
    
#     yield app

