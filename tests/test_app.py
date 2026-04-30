import os
import pytest

# Skip tests if flask is not installed
pytest.importorskip("flask")

from html2md.app import get_host_port, DEFAULT_PORT


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port returns defaults when no env vars are set."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)

    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT


def test_get_host_port_valid_values(monkeypatch):
    """Test get_host_port returns configured values when valid env vars are set."""
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8080")

    host, port = get_host_port()
    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid_port_fallback(monkeypatch, capsys):
    """Test get_host_port falls back and warns when PORT is invalid."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.setenv("PORT", "invalid_port")

    host, port = get_host_port()

    # Check return values
    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT

    # Check warning message
    captured = capsys.readouterr()
    expected_warning = "Warning: Invalid PORT environment variable value 'invalid_port'; falling back to default 10000."
    assert expected_warning in captured.out
