import os
import pytest

flask = pytest.importorskip("flask")

from unittest.mock import patch
from html2md.app import get_host_port, DEFAULT_PORT

def test_get_host_port_defaults():
    """Test get_host_port returns secure defaults when env vars are absent."""
    with patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == '127.0.0.1'
        assert port == DEFAULT_PORT

def test_get_host_port_custom():
    """Test get_host_port respects HOST and PORT env vars."""
    env = {'HOST': '192.168.1.100', 'PORT': '8080'}
    with patch.dict(os.environ, env, clear=True):
        host, port = get_host_port()
        assert host == '192.168.1.100'
        assert port == 8080

def test_get_host_port_invalid_port():
    """Test get_host_port handles invalid PORT values."""
    env = {'PORT': 'not-a-number'}
    with patch.dict(os.environ, env, clear=True):
        host, port = get_host_port()
        assert host == '127.0.0.1'
        assert port == DEFAULT_PORT
