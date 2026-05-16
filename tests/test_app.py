import pytest
import os
import json

flask = pytest.importorskip("flask")

from html2md.app import app, get_host_port, DEFAULT_PORT
from html2md import __version__


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data == {"status": "ok", "service": "html2md", "version": __version__}


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port with default environment variables."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT


def test_get_host_port_custom(monkeypatch):
    """Test get_host_port with custom environment variables."""
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8080")
    host, port = get_host_port()
    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test get_host_port with an invalid port value."""
    monkeypatch.setenv("PORT", "invalid_port")
    host, port = get_host_port()
    assert port == DEFAULT_PORT

    # Verify the warning was printed
    captured = capsys.readouterr()
    assert "Warning: Invalid PORT environment variable value" in captured.out
    assert "falling back to default" in captured.out
