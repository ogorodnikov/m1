import pytest

from tempfile import NamedTemporaryFile

from core import config


def test_configuration():
    
    with NamedTemporaryFile() as temporary_file:
        
        configuration = config.Config(log_file_path=temporary_file.name)
        
        logs = temporary_file.read().decode("utf-8")
        
        assert "LOGGING initiated" in logs
        

def test_print_environ():
    
    configuration = config.Config()
    configuration.print_environ()