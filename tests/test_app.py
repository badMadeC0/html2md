"""Tests for the Flask application module."""

import os
from unittest import mock

import pytest

flask = pytest.importorskip("flask")

from html2md import __version__
from html2md.app import app, get_host_port


@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the /health endpoint returns correct status and version."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {
        "status": "ok",
        "service": "html2md",
        "version": __version__
    }


def test_get_host_port_defaults():
    """Test get_host_port returns defaults when env vars are unset."""
    with mock.patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == 10000


def test_get_host_port_custom():
    """Test get_host_port respects valid environment variables."""
    with mock.patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "8080"}):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    """Test get_host_port falls back to default on invalid port."""
    with mock.patch.dict(os.environ, {"PORT": "invalid"}):
        host, port = get_host_port()
        assert port == 10000

        # Check that warning was printed
        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'invalid'" in captured.out
