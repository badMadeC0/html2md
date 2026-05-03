import os
from unittest import mock

import pytest

# Tests in tests/test_app.py require the flask library and are skipped automatically if it is not installed
pytest.importorskip("flask")

from html2md.app import get_host_port


def test_get_host_port_defaults():
    with mock.patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == '0.0.0.0'
        assert port == 10000


def test_get_host_port_valid_values():
    with mock.patch.dict(os.environ, {'PORT': '8080', 'HOST': '127.0.0.1'}, clear=True):
        host, port = get_host_port()
        assert host == '127.0.0.1'
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    with mock.patch.dict(os.environ, {'PORT': 'invalid_port', 'HOST': '0.0.0.0'}, clear=True):
        host, port = get_host_port()
        assert host == '0.0.0.0'
        assert port == 10000

        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'invalid_port'" in captured.out
