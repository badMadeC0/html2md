"""Tests for the html2md.app module."""
import importlib

import pytest

from html2md import __version__  # type: ignore

pytest.importorskip('flask')


def test_health_endpoint():
    """Test the health endpoint."""
    flask_app_module = importlib.import_module('html2md.app')
    client = flask_app_module.app.test_client()

    response = client.get('/health')

    assert response.status_code == 200
    from html2md import __version__
    assert response.get_json() == {'status': 'ok', 'service': 'html2md', 'version': __version__}


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port defaults."""
    monkeypatch.delenv('HOST', raising=False)
    monkeypatch.delenv('PORT', raising=False)

    flask_app_module = importlib.import_module('html2md.app')
    host, port = flask_app_module.get_host_port()

    assert host == '127.0.0.1'
    assert port == 10000


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test get_host_port with invalid port."""
    monkeypatch.setenv('HOST', '127.0.0.1')
    monkeypatch.setenv('PORT', 'invalid')

    flask_app_module = importlib.import_module('html2md.app')
    host, port = flask_app_module.get_host_port()

    assert host == '0.0.0.0'
    assert port == 10000
    assert 'Invalid PORT environment variable value' in capsys.readouterr().out
