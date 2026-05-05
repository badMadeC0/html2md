import os
import sys
import pytest
from unittest.mock import MagicMock, patch

try:
    import flask
    from html2md.app import get_host_port, DEFAULT_PORT
except ImportError:
    pytest.skip("flask is not installed", allow_module_level=True)


def test_get_host_port_defaults():
    with patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT


def test_get_host_port_custom():
    with patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "8080"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    with patch.dict(os.environ, {"PORT": "not_a_number"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert (
            "Warning: Invalid PORT environment variable value 'not_a_number'"
            in captured.out
        )
