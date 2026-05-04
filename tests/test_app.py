"""Tests for the Flask application module."""

import os
from unittest import mock

import pytest

flask = pytest.importorskip("flask")

from html2md.app import DEFAULT_PORT, get_host_port


def test_get_host_port_defaults():
    """Test get_host_port returns defaults when no env vars are set."""
    with mock.patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == '0.0.0.0'
        assert port == DEFAULT_PORT


def test_get_host_port_custom_values():
    """Test get_host_port returns custom values when valid env vars are set."""
    env = {'HOST': '127.0.0.1', 'PORT': '8080'}
    with mock.patch.dict(os.environ, env, clear=True):
        host, port = get_host_port()
        assert host == '127.0.0.1'
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    """Test get_host_port falls back to default port when PORT is invalid."""
    env = {'HOST': '192.168.1.1', 'PORT': 'invalid'}
    with mock.patch.dict(os.environ, env, clear=True):
        host, port = get_host_port()
        assert host == '192.168.1.1'
        assert port == DEFAULT_PORT

        # Verify the warning was printed
        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value 'invalid'; falling back to default 10000." in captured.out


def test_get_host_port_empty_port(capsys):
    """Test get_host_port falls back to default port when PORT is empty string."""
    env = {'PORT': ''}
    with mock.patch.dict(os.environ, env, clear=True):
        host, port = get_host_port()
        assert host == '0.0.0.0'
        assert port == DEFAULT_PORT

        # Verify the warning was printed
        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value ''; falling back to default 10000." in captured.out
