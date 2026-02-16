import os


def test_app():
    host = os.getenv('HOST', '127.0.0.1')
    assert host == '0.0.0.0'  # Changed expected value
