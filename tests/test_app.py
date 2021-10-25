import os
import pytest

from core.app import create_app


def test_start_telegram_bot(app):
    
    app.start_telegram_bot()
    assert app.config['TELEGRAM_BOT_STATE'] == 'Running'
    

def test_stop_telegram_bot(app):
    
    app.stop_telegram_bot()
    assert app.config['TELEGRAM_BOT_STATE'] == 'Stopped'


def test_run_with_gunicorn(app):
    app.run_with_gunicorn(test_mode=True)
    
    
def test_run_with_development_server(app):
    app.run_with_development_server(test_mode=True)


def test_clear_figures_folder(app):
    
    test_figure_path = os.path.join(app.static_folder, 'figures/test_figure.png')
    open(test_figure_path, 'w')
    
    app.clear_figures_folder()
    

def test_termination_handler(app):
    app.termination_handler(signal='test_signal', frame='test_frame')
    
    
def test_exit_application(app):
    app.exit_application(test_mode=True)
    
    
###   Fixtures
    
@pytest.fixture(scope="module")
def app():
    
    app = create_app()

    app.testing = True
    
    yield app
        
    app.stop_runner()