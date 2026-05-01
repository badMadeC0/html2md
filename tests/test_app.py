"""Tests for the Flask application."""

import pytest

try:
    import flask

    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

if HAS_FLASK:
    from html2md.app import app
    from html2md import __version__

pytestmark = pytest.mark.skipif(not HAS_FLASK, reason="Flask is not installed")


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    if not HAS_FLASK:
        yield None
        return
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the /health endpoint returns correct status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "html2md"
    assert data["version"] == __version__


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port with missing environment variables."""
    if not HAS_FLASK:
        pytest.skip("Flask is not installed")
    from html2md.app import get_host_port

    # Remove variables if they exist
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HOST", raising=False)

    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == 10000


def test_get_host_port_custom(monkeypatch):
    """Test get_host_port with valid environment variables."""
    if not HAS_FLASK:
        pytest.skip("Flask is not installed")
    from html2md.app import get_host_port

    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("HOST", "127.0.0.1")

    host, port = get_host_port()
    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test get_host_port with invalid PORT value."""
    if not HAS_FLASK:
        pytest.skip("Flask is not installed")
    from html2md.app import get_host_port

    monkeypatch.setenv("PORT", "not-a-number")

    host, port = get_host_port()
    assert port == 10000

    # Check that warning was printed
    captured = capsys.readouterr()
    assert "Invalid PORT environment variable value 'not-a-number'" in captured.out
