"""Tests for the Flask application module."""

import os
from unittest import mock

import pytest

try:
    import flask
except ImportError:
    pytest.skip("Flask is not installed", allow_module_level=True)

from html2md.app import DEFAULT_PORT, get_host_port


def test_get_host_port_defaults():
    """Test getting host and port when no env vars are set."""
    with mock.patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT


def test_get_host_port_custom_values():
    """Test getting host and port with custom env vars."""
    with mock.patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "8080"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == 8080


def test_get_host_port_invalid_port_fallback(capsys):
    """Test fallback to default port when PORT is invalid."""
    with mock.patch.dict(os.environ, {"PORT": "not_an_int"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT
        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
