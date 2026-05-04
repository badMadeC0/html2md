import os
import pytest
from unittest.mock import patch

pytest.importorskip("flask")

from html2md.app import get_host_port, DEFAULT_PORT


def test_get_host_port_defaults():
    """Test get_host_port with no environment variables set."""
    with patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT


def test_get_host_port_custom_port():
    """Test get_host_port with a valid custom PORT."""
    with patch.dict(os.environ, {"PORT": "8080"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    """Test get_host_port with an invalid PORT value."""
    with patch.dict(os.environ, {"PORT": "invalid_port"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'invalid_port'" in captured.out


def test_get_host_port_custom_host():
    """Test get_host_port with a custom HOST."""
    with patch.dict(os.environ, {"HOST": "127.0.0.1"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == DEFAULT_PORT


def test_get_host_port_custom_host_and_port():
    """Test get_host_port with both custom HOST and PORT."""
    with patch.dict(os.environ, {"HOST": "192.168.1.100", "PORT": "9000"}, clear=True):
        host, port = get_host_port()
        assert host == "192.168.1.100"
        assert port == 9000
