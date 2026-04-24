import os
import pytest
from unittest.mock import patch

try:
    from html2md.app import get_host_port, DEFAULT_PORT

    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

pytestmark = pytest.mark.skipif(not HAS_FLASK, reason="flask is not installed")


def test_get_host_port_defaults():
    with patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT


def test_get_host_port_custom_port():
    with patch.dict(os.environ, {"PORT": "8080"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    with patch.dict(os.environ, {"PORT": "invalid"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT
        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'invalid'" in captured.out


def test_get_host_port_custom_host():
    with patch.dict(os.environ, {"HOST": "127.0.0.1"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == DEFAULT_PORT


def test_get_host_port_custom_host_and_port():
    with patch.dict(os.environ, {"HOST": "192.168.1.1", "PORT": "9000"}, clear=True):
        host, port = get_host_port()
        assert host == "192.168.1.1"
        assert port == 9000
