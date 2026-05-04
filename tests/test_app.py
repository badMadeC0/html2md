"""Tests for the flask application."""

import pytest

try:
    from html2md.app import get_host_port, DEFAULT_PORT

    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

pytestmark = pytest.mark.skipif(not HAS_FLASK, reason="flask is required for app tests")


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port with no environment variables."""
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HOST", raising=False)
    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT


def test_get_host_port_valid_port(monkeypatch):
    """Test get_host_port with a valid PORT environment variable."""
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.delenv("HOST", raising=False)
    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == 8080


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test get_host_port with an invalid PORT environment variable."""
    monkeypatch.setenv("PORT", "invalid")
    monkeypatch.delenv("HOST", raising=False)
    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT

    captured = capsys.readouterr()
    assert "Warning: Invalid PORT environment variable value 'invalid'" in captured.out


def test_get_host_port_custom_host(monkeypatch):
    """Test get_host_port with a custom HOST environment variable."""
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.setenv("HOST", "127.0.0.1")
    host, port = get_host_port()
    assert host == "127.0.0.1"
    assert port == DEFAULT_PORT


def test_get_host_port_both_custom(monkeypatch):
    """Test get_host_port with both custom PORT and HOST."""
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("HOST", "localhost")
    host, port = get_host_port()
    assert host == "localhost"
    assert port == 9000
