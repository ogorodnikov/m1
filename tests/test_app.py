import pytest

from core.app import FlaskApp
from core.app import create_app

from core.gunicorn.app import GunicornApp


###   Run   ###

def test_run_with_gunicorn(app):
    app.run_with_gunicorn()
    
def test_run_with_development_server(app):
    app.run_with_development_server()


###   Service   ###

def test_clear_figures_folder(app):
    app.clear_figures_folder()

def test_termination_handler(app):
    app.termination_handler(signal='test_signal', frame='test_frame')
    
def test_exit_application(app):
    app.exit_application(test_mode=True)
    
    
###   Gunicorn   ###

def test_gunicorn_app_options():
    gunicorn_app = GunicornApp(None, options={'config': 'test_config'})
    
def test_gunicorn_app_load():
    gunicorn_app = GunicornApp(None)
    gunicorn_app.load()


###   Fixtures   ###
    
@pytest.fixture(scope="module")
def app():
    
    app = create_app()
    app.testing = True
    
    yield app

@pytest.fixture(autouse=True)
def set_mocks(monkeypatch, stub):
    
    monkeypatch.setattr(FlaskApp, 'run', stub)
    monkeypatch.setattr(GunicornApp, 'run', stub)
    
    monkeypatch.setattr('core.app.os.remove', stub)