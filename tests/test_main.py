# def test_logging(users, caplog):
    
#     message = "Test log :)"
#     users.log(message)
#     print('Print test')
    
#     logging.getLogger('users').info("log test!")
    
#     print(f"caplog.text {caplog.text}")
    
#     print(f"caplog.records {caplog.records}")
    
#     print(f"caplog.get_records('setup') {caplog.get_records('setup')}")
#     print(f"caplog.get_records('call') {caplog.get_records('call')}")
#     print(f"caplog.get_records('teardown') {caplog.get_records('teardown')}")
    
    
    
    # raise 

    # assert message in capture_output["stderr"]    

# def test_log(users, capture_output):
    
#     message = "Test log :)"
#     users.log(message)
#     assert message in capture_output["stderr"]


# def test_log_to_file():
    
#     with NamedTemporaryFile() as temporary_file:
        
#         configuration = config.Config(log_file_path=temporary_file.name)
        
#         logs = temporary_file.read().decode("utf-8")
        
#         assert "LOGGING initiated" in logs


# def test_print_environ(run_config):
#     run_config.print_environ()



# ###   Fixtures   ###

# @pytest.fixture
# def capture_output(monkeypatch):
    
#     buffer = {"stderr": ""}

#     def capture(message):
#         buffer["stderr"] += message

#     monkeypatch.setattr(sys.stderr, 'write', capture)

#     return buffer