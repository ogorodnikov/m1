import pytest

# from core import config


# General tests

def test_config():
    
    from core import config
    
    configuration = config.Config()

    
# def test_print_environ(alt_run_config):
    
#     alt_run_config.print_environ()
    


# ###   Fixtures
    
# @pytest.fixture(scope="module")
# def alt_run_config():
    
#     configuration = config.Config()

#     yield configuration