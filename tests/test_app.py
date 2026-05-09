import os
import pytest
from unittest.mock import patch

try:
    import flask

    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

if HAS_FLASK:
    from html2md.app import get_host_port, DEFAULT_PORT, app, __version__
else:
    pytest.skip("Flask is not installed", allow_module_level=True)


def test_get_host_port_defaults():
    with patch.dict(os.environ, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT


def test_get_host_port_valid_env():
    with patch.dict(os.environ, {"PORT": "8080", "HOST": "127.0.0.1"}):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    with patch.dict(os.environ, {"PORT": "invalid"}):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT
        captured = capsys.readouterr()
        assert (
            f"Warning: Invalid PORT environment variable value 'invalid'; falling back to default {DEFAULT_PORT}."
            in captured.out
        )


def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "service": "html2md",
        "version": __version__,
    }
