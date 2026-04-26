"""Tests for the flask app module."""

import os
from unittest.mock import patch

import pytest

pytest.importorskip("flask")

from html2md.app import get_host_port, DEFAULT_PORT


def test_get_host_port_defaults():
    """Test get_host_port when no environment variables are set."""
    with patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT


def test_get_host_port_valid_port():
    """Test get_host_port with a valid PORT environment variable."""
    with patch.dict(os.environ, {"PORT": "8080"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    """Test get_host_port with an invalid PORT environment variable."""
    with patch.dict(os.environ, {"PORT": "invalid"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert (
            "Warning: Invalid PORT environment variable value 'invalid'" in captured.out
        )


def test_get_host_port_custom_host():
    """Test get_host_port with a custom HOST environment variable."""
    with patch.dict(os.environ, {"HOST": "127.0.0.1"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == DEFAULT_PORT


def test_get_host_port_custom_host_and_port():
    """Test get_host_port with both HOST and PORT environment variables."""
    with patch.dict(os.environ, {"HOST": "192.168.1.1", "PORT": "9000"}, clear=True):
        host, port = get_host_port()
        assert host == "192.168.1.1"
        assert port == 9000

def test_get_host_port_out_of_range(capsys):
    """Test get_host_port with out of range PORT values."""
    with patch.dict(os.environ, {"PORT": "70000"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT
        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value '70000'" in captured.out

    with patch.dict(os.environ, {"PORT": "0"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT
        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value '0'" in captured.out
