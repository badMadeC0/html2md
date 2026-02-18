"""Tests for the Flask app endpoints and configuration helpers."""
import importlib

import pytest

pytest.importorskip('flask')


def test_health_endpoint():
    """Verify the /health endpoint returns a JSON OK response."""
    flask_app_module = importlib.import_module('html2md.app')
    client = flask_app_module.app.test_client()

    response = client.get('/health')

    assert response.status_code == 200
    json_response = response.get_json()
    assert json_response['status'] == 'ok'
    assert json_response['version'] == flask_app_module.__version__
    assert json_response['service'] == 'html2md'


def test_get_host_port_defaults(monkeypatch: pytest.MonkeyPatch):
    """Ensure default HOST/PORT are used when env vars are missing."""
    monkeypatch.delenv('HOST', raising=False)
    monkeypatch.delenv('PORT', raising=False)

    flask_app_module = importlib.import_module('html2md.app')
    host, port = flask_app_module.get_host_port()

    assert host == '0.0.0.0'
    assert port == 10000


def test_get_host_port_invalid_port(
        monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """Ensure invalid PORT falls back to default and logs a warning."""
    monkeypatch.setenv('HOST', '0.0.0.0')
    monkeypatch.setenv('PORT', 'invalid')

    flask_app_module = importlib.import_module('html2md.app')
    host, port = flask_app_module.get_host_port()

    assert host == '0.0.0.0'
    assert port == 10000
    assert 'Invalid PORT environment variable value' in capsys.readouterr().out
