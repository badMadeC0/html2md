"""Tests for the Flask application module."""

import os
from unittest import mock

import pytest

pytest.importorskip("flask")

from html2md.app import get_host_port, DEFAULT_PORT


def test_get_host_port_defaults():
    """Test get_host_port with no environment variables set."""
    with mock.patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT


def test_get_host_port_valid_port():
    """Test get_host_port with a valid PORT environment variable."""
    with mock.patch.dict(os.environ, {"PORT": "8080"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    """Test get_host_port with an invalid PORT falls back to default and warns."""
    with mock.patch.dict(os.environ, {"PORT": "invalid"}, clear=True):
        host, port = get_host_port()

        # Check return values
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT

        # Check stdout for the warning message
        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'invalid'" in captured.out
        assert str(DEFAULT_PORT) in captured.out


def test_get_host_port_custom_host():
    """Test get_host_port with a custom HOST environment variable."""
    with mock.patch.dict(os.environ, {"HOST": "127.0.0.1"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == DEFAULT_PORT


def test_get_host_port_custom_host_and_port():
    """Test get_host_port with both HOST and valid PORT environment variables."""
    with mock.patch.dict(os.environ, {"HOST": "localhost", "PORT": "5000"}, clear=True):
        host, port = get_host_port()
        assert host == "localhost"
        assert port == 5000
