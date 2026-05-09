"""Tests for html2md.app configuration helpers."""
import pytest

pytest.importorskip("flask")

from html2md.app import DEFAULT_PORT, get_host_port  # noqa: E402


def test_get_host_port_defaults(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HOST", raising=False)

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT


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
    assert port == DEFAULT_PORT

    captured = capsys.readouterr()
    assert "Warning: Invalid PORT" in captured.out
    assert "invalid" in captured.out
    assert str(DEFAULT_PORT) in captured.out
