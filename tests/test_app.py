"""Tests for the Flask application."""

import os
import pytest

# Skip the entire module if Flask is not installed
pytest.importorskip("flask")

# Now we can safely import from html2md.app
from html2md.app import app, get_host_port
from html2md import __version__


@pytest.fixture
def client():
    """Create a Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the /health endpoint returns the expected status and JSON body."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert data["status"] == "ok"
    assert data["service"] == "html2md"
    assert data["version"] == __version__


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port returns default values when env vars are absent."""
    # Ensure environment variables are not set
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)

    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == 10000


def test_get_host_port_custom_values(monkeypatch):
    """Test get_host_port with custom valid HOST and PORT."""
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8080")

    host, port = get_host_port()
    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test get_host_port handles invalid PORT by falling back to default."""
    monkeypatch.setenv("PORT", "invalid")

    host, port = get_host_port()
    assert port == 10000

    # Check that a warning was printed
    captured = capsys.readouterr()
    assert "Warning: Invalid PORT environment variable value" in captured.out
    assert "'invalid'" in captured.out
