"""Tests for the Flask application module."""

from __future__ import annotations

import importlib
import os
import sys
from unittest import mock


def _load_app_module():
    """Import html2md.app with a stub Flask module for CI environments."""
    sys.modules.pop("html2md.app", None)
    flask_stub = mock.MagicMock()
    flask_stub.Flask.return_value.route.return_value = lambda func: func
    with mock.patch.dict(sys.modules, {"flask": flask_stub}, clear=False):
        return importlib.import_module("html2md.app")


def test_get_host_port_defaults():
    """Test get_host_port with no environment variables set."""
    app = _load_app_module()
    with mock.patch.dict(os.environ, {}, clear=True):
        host, port = app.get_host_port()
        assert host == "0.0.0.0"
        assert port == app.DEFAULT_PORT


def test_get_host_port_valid_port():
    """Test get_host_port with a valid PORT environment variable."""
    app = _load_app_module()
    with mock.patch.dict(os.environ, {"PORT": "8080"}, clear=True):
        host, port = app.get_host_port()
        assert host == "0.0.0.0"
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    """Test get_host_port with an invalid PORT falls back to default and warns."""
    app = _load_app_module()
    with mock.patch.dict(os.environ, {"PORT": "invalid"}, clear=True):
        host, port = app.get_host_port()

        # Check return values
        assert host == "0.0.0.0"
        assert port == app.DEFAULT_PORT

        # Check stdout for the warning message
        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'invalid'" in captured.out
        assert str(app.DEFAULT_PORT) in captured.out


def test_get_host_port_custom_host():
    """Test get_host_port with a custom HOST environment variable."""
    app = _load_app_module()
    with mock.patch.dict(os.environ, {"HOST": "127.0.0.1"}, clear=True):
        host, port = app.get_host_port()
        assert host == "127.0.0.1"
        assert port == app.DEFAULT_PORT


def test_get_host_port_custom_host_and_port():
    """Test get_host_port with both HOST and valid PORT environment variables."""
    app = _load_app_module()
    with mock.patch.dict(os.environ, {"HOST": "localhost", "PORT": "5000"}, clear=True):
        host, port = app.get_host_port()
        assert host == "localhost"
        assert port == 5000
