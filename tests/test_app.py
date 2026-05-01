import os
import pytest
from unittest.mock import patch
pytest.importorskip("flask")
from html2md.app import get_host_port, DEFAULT_PORT

def test_get_host_port_defaults():
    with patch.dict(os.environ, clear=True):
        host, port = get_host_port()
        assert host == '0.0.0.0'
        assert port == DEFAULT_PORT

def test_get_host_port_valid_env():
    env = {'HOST': '127.0.0.1', 'PORT': '8080'}
    with patch.dict(os.environ, env, clear=True):
        host, port = get_host_port()
        assert host == '127.0.0.1'
        assert port == 8080

def test_get_host_port_invalid_port_non_numeric(capsys):
    env = {'PORT': 'not_a_number'}
    with patch.dict(os.environ, env, clear=True):
        host, port = get_host_port()
        assert host == '0.0.0.0'
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'not_a_number'" in captured.out
        assert f"falling back to default {DEFAULT_PORT}" in captured.out

def test_get_host_port_invalid_port_empty_string(capsys):
    env = {'PORT': ''}
    with patch.dict(os.environ, env, clear=True):
        host, port = get_host_port()
        assert host == '0.0.0.0'
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "''" in captured.out
        assert f"falling back to default {DEFAULT_PORT}" in captured.out

@pytest.mark.parametrize("invalid_port", ["-1", "0", "65536", "100000"])
def test_get_host_port_out_of_bounds_port(capsys, invalid_port):
    env = {'PORT': invalid_port}
    with patch.dict(os.environ, env, clear=True):
        host, port = get_host_port()
        assert host == '0.0.0.0'
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert f"'{invalid_port}'" in captured.out
        assert f"falling back to default {DEFAULT_PORT}" in captured.out
