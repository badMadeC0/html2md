"""Security tests for the Flask application defaults."""

import os
from unittest.mock import patch
from html2md.app import get_host_port, DEFAULT_PORT


def test_get_host_port_defaults():
    """Verify default host and port when no environment variables are set."""
    with patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == '127.0.0.1'
        assert port == DEFAULT_PORT


def test_get_host_port_from_env():
    """Verify host and port are correctly read from environment variables."""
    with patch.dict(os.environ, {'HOST': '10.0.0.1', 'PORT': '8080'}):
        host, port = get_host_port()
        assert host == '10.0.0.1'
        assert port == 8080


def test_get_host_port_security_warning_0000(capsys):
    """Verify security warning when binding to 0.0.0.0."""
    with patch.dict(os.environ, {'HOST': '0.0.0.0'}):
        host, port = get_host_port()
        assert host == '0.0.0.0'
        captured = capsys.readouterr()
        assert 'Security Warning: Host is set to 0.0.0.0' in captured.out


def test_get_host_port_invalid_port(capsys):
    """Verify fallback when an invalid port is provided."""
    with patch.dict(os.environ, {'PORT': 'invalid'}):
        _, port = get_host_port()
        assert port == DEFAULT_PORT
        captured = capsys.readouterr()
        assert 'Warning: Invalid PORT environment variable value' in captured.out
