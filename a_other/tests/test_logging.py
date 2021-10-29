import pytest


def test_log(users, capture_output):
    
    message = "Test log :)"
    users.log(message)
    assert message in capture_output["stderr"]

@pytest.fixture
def capture_output(monkeypatch):
    
    buffer = {"stderr": ""}

    def capture(message):
        buffer["stderr"] += message

    monkeypatch.setattr(sys.stderr, 'write', capture)

    return buffer



    print(f"caplog.text {caplog.text}")
    print(f"caplog.records {caplog.records}")
    print(f"caplog.record_tuples {caplog.record_tuples}")