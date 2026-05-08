"""Tests for html2md web application configuration helpers."""

from html2md.app_config import DEFAULT_PORT, get_host_port


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port returns defaults when env vars are not set."""
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HOST", raising=False)

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT


def test_get_host_port_valid_values(monkeypatch):
    """Test get_host_port returns environment values when they are valid."""
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("HOST", "127.0.0.1")

    host, port = get_host_port()

    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test get_host_port handles invalid port value and falls back to default."""
    monkeypatch.setenv("PORT", "invalid")
    monkeypatch.delenv("HOST", raising=False)

    host, port = get_host_port()

    # Check return values
    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT

    # Check warning printed to stdout
    captured = capsys.readouterr()
    expected_warning = (
        f"Warning: Invalid PORT environment variable value 'invalid'; "
        f"falling back to default {DEFAULT_PORT}."
    )
    assert expected_warning in captured.out
