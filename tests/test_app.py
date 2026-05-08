import importlib
import sys
from unittest.mock import MagicMock

sys.modules.setdefault("flask", MagicMock())
app_module = importlib.import_module("html2md.app")
DEFAULT_PORT = app_module.DEFAULT_PORT
get_host_port = app_module.get_host_port


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port when no environment variables are set."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT


def test_get_host_port_custom_values(monkeypatch):
    """Test get_host_port with valid custom environment variables."""
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8080")

    host, port = get_host_port()

    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test get_host_port with an invalid PORT value."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.setenv("PORT", "invalid_port")

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT

    captured = capsys.readouterr()
    expected_warning = (
        "Warning: Invalid PORT environment variable value 'invalid_port'; "
        f"falling back to default {DEFAULT_PORT}.\n"
    )
    assert captured.out == expected_warning
