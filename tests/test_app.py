"""Tests for the Flask application module."""
import pytest

pytest.importorskip('flask')

# pylint: disable=wrong-import-position
from html2md.app import app, get_host_port  # type: ignore[import-untyped]


def test_health_endpoint():
    """Test the health check endpoint returns 200 OK."""
    client = app.test_client()

    response = client.get('/health')

    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port returns defaults when env vars are missing."""
    monkeypatch.delenv('HOST', raising=False)
    monkeypatch.delenv('PORT', raising=False)

    host, port = get_host_port()

    assert host == '127.0.0.1'
    assert port == 10000


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test get_host_port handles invalid PORT environment variable."""
    monkeypatch.setenv('HOST', '127.0.0.1')
    monkeypatch.setenv('PORT', 'invalid')

    host, port = get_host_port()

    assert host == '127.0.0.1'
    assert port == 10000
    assert 'Invalid PORT environment variable value' in capsys.readouterr().out
