import os
from unittest import mock

from html2md.app_config import DEFAULT_HOST, DEFAULT_PORT, get_host_port


def test_get_host_port_defaults():
    with mock.patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == DEFAULT_HOST
        assert port == DEFAULT_PORT


def test_get_host_port_valid_values():
    with mock.patch.dict(os.environ, {'PORT': '8080', 'HOST': '127.0.0.1'}, clear=True):
        host, port = get_host_port()
        assert host == '127.0.0.1'
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    with mock.patch.dict(os.environ, {'PORT': 'invalid_port', 'HOST': '0.0.0.0'}, clear=True):
        host, port = get_host_port()
        assert host == DEFAULT_HOST
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'invalid_port'" in captured.out
