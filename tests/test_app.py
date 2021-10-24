import pytest

from core.app import create_app
from core.gunicorn.app import GunicornApp


def test_home(client):

    response = client.get('/')
    
    print(response)
    # print(response.data)
    
    assert b'M1 Core Service' in response.data


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


def test_start_logging(app):
    

    with NamedTemporaryFile() as temporary_file:
        app.start_log_file(temporary_file.name)
        assert "LOGGING initiated" in temporary_file.read().decode("utf-8")
        
def test_clear_figures_folder(app):
    
    app.clear_figures_folder()


@pytest.fixture(scope="module")
def app():
    
    app = create_app()

    app.testing = True
    
    yield app
        
    app.stop_runner()


@pytest.fixture(scope="module")
def client():
    
    app = create_app()

    app.testing = True
    
    with app.test_client() as client:
        yield client
        
    app.stop_runner()
    