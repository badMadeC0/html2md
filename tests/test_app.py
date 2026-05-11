"""Tests for the Flask application module."""

import pytest

# Skip all tests in this module if flask is not installed
pytest.importorskip("flask")

from html2md.app import get_host_port


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port when no environment variables are set."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == 10000


def test_get_host_port_with_values(monkeypatch):
    """Test get_host_port with valid HOST and PORT environment variables."""
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8080")
    host, port = get_host_port()
    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test get_host_port with an invalid PORT value."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.setenv("PORT", "not-a-number")
    host, port = get_host_port()

    # Should fall back to defaults
    assert host == "0.0.0.0"
    assert port == 10000

    # Check that a warning was printed
    captured = capsys.readouterr()
    assert "Warning: Invalid PORT environment variable value" in captured.out
    assert "'not-a-number'" in captured.out
