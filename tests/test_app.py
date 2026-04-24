import os
import pytest
from flask import Flask
from html2md.app import app, get_host_port
from html2md import __version__


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test that the /health endpoint returns a 200 OK and expected JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "html2md"
    assert data["version"] == __version__


def test_get_host_port_default(monkeypatch):
    """Test get_host_port with missing environment variables."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == 10000


def test_get_host_port_env(monkeypatch):
    """Test get_host_port with valid environment variables."""
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8080")
    host, port = get_host_port()
    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid(monkeypatch):
    """Test get_host_port with an invalid PORT environment variable."""
    monkeypatch.setenv("PORT", "invalid")
    host, port = get_host_port()
    assert port == 10000
