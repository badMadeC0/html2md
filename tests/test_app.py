import os
import pytest

try:
    import flask
except ImportError:
    pytest.skip("flask is not installed", allow_module_level=True)

from html2md.app import get_host_port


def test_get_host_port_defaults(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HOST", raising=False)

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == 10000


def test_get_host_port_valid_values(monkeypatch):
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("HOST", "127.0.0.1")

    host, port = get_host_port()

    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid_port(monkeypatch, capsys):
    monkeypatch.setenv("PORT", "invalid")
    monkeypatch.delenv("HOST", raising=False)

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == 10000

    captured = capsys.readouterr()
    assert (
        "Warning: Invalid PORT environment variable value 'invalid'; falling back to default 10000."
        in captured.out
    )
