"""Tests for optional web app server configuration."""

from html2md.server_config import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEPLOY_HOST,
    get_host_port,
)

def test_get_host_port_default(monkeypatch):
    """Return localhost and the default port for local runs without env vars."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)

    hostname, port = get_host_port()
    assert hostname == DEFAULT_HOST
    assert port == DEFAULT_PORT


def test_get_host_port_custom_host(monkeypatch):
    """Respect an explicit HOST environment variable."""
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.delenv("PORT", raising=False)

    hostname, port = get_host_port()
    assert hostname == "0.0.0.0"
    assert port == DEFAULT_PORT


def test_get_host_port_port_only_uses_deploy_host(monkeypatch):
    """Bind to all interfaces when a PaaS-style PORT is provided without HOST."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.setenv("PORT", "8080")

    hostname, port = get_host_port()

    assert hostname == DEPLOY_HOST
    assert port == 8080


def test_get_host_port_empty_host_falls_back_to_contextual_default(monkeypatch):
    """Do not pass an empty HOST through to Flask/Werkzeug."""
    monkeypatch.setenv("HOST", "")
    monkeypatch.delenv("PORT", raising=False)

    hostname, port = get_host_port()

    assert hostname == DEFAULT_HOST
    assert port == DEFAULT_PORT


def test_get_host_port_empty_host_with_port_uses_deploy_host(monkeypatch):
    """Treat an empty HOST like missing HOST for PaaS-style PORT-only launches."""
    monkeypatch.setenv("HOST", "")
    monkeypatch.setenv("PORT", "18080")

    hostname, port = get_host_port()

    assert hostname == DEPLOY_HOST
    assert port == 18080


def test_get_host_port_invalid_port_is_treated_as_missing(monkeypatch):
    """Invalid PORT should not trigger deploy host binding."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.setenv("PORT", "abc")

    hostname, port = get_host_port()

    assert hostname == DEFAULT_HOST
    assert port == DEFAULT_PORT
