"""Tests for the Flask application."""

import importlib

import pytest

pytest.importorskip('flask')


def test_health_endpoint():
    """Test the health check endpoint."""
    flask_app_module = importlib.import_module('html2md.app')
    client = flask_app_module.app.test_client()

    response = client.get('/health')

    assert response.status_code == 200
    json_response = response.get_json()
    assert json_response['status'] == 'ok'
    assert json_response['service'] == 'html2md'
    assert json_response['version'] == flask_app_module.__version__


def test_get_host_port_defaults(monkeypatch):
    """Test getting host and port with defaults."""
    monkeypatch.delenv('HOST', raising=False)
    monkeypatch.delenv('PORT', raising=False)

    flask_app_module = importlib.import_module('html2md.app')
    host, port = flask_app_module.get_host_port()

    assert host == '127.0.0.1'
    assert port == 10000


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test getting host and port with invalid port environment variable."""
    monkeypatch.setenv('HOST', '0.0.0.0')
    monkeypatch.setenv('PORT', 'invalid')

    flask_app_module = importlib.import_module('html2md.app')
    host, port = flask_app_module.get_host_port()

    assert host == '0.0.0.0'
    assert port == 10000
    assert 'Invalid PORT environment variable value' in capsys.readouterr().err
