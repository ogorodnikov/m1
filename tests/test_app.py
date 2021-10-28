import os
import pytest

from core.app import FlaskApp
from core.app import create_app

from core.gunicorn.app import GunicornApp
from core.gunicorn.config import post_worker_init


def test_run_with_gunicorn(app):
    app.run_with_gunicorn()
    
def test_run_with_development_server(app):
    app.run_with_development_server()


def test_clear_figures_folder(app):
    
    test_figure_path = os.path.join(app.static_folder, 'figures/test_figure.png')
    open(test_figure_path, 'w')
    
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

def test_post_worker_init():
    post_worker_init(None)
    
    
###   Fixtures   ###
    
@pytest.fixture(scope="module")
def app():
    
    app = create_app()
    app.testing = True
    
    yield app
        
    # app.stop_runner()
    

@pytest.fixture(autouse=True)
def mocks(monkeypatch):
    
    def stub(*args, **kwargs):
        pass
    
    monkeypatch.setattr(FlaskApp, 'run', stub)
    monkeypatch.setattr(GunicornApp, 'run', stub)