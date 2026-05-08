"""Tests for the Flask application module."""

from html2md.app import DEFAULT_PORT, get_host_port


def test_get_host_port_defaults(monkeypatch):
    """Test get_host_port when no environment variables are set."""
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HOST", raising=False)

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT


def test_get_host_port_valid_values(monkeypatch):
    """Test get_host_port with valid PORT and HOST."""
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("HOST", "127.0.0.1")

    host, port = get_host_port()

    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid_port(monkeypatch, capsys):
    """Test get_host_port with an invalid PORT value."""
    monkeypatch.setenv("PORT", "not-a-number")
    monkeypatch.delenv("HOST", raising=False)

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT

    captured = capsys.readouterr()
    assert (
        "Warning: Invalid PORT environment variable value 'not-a-number'"
        in captured.out
    )
    assert f"falling back to default {DEFAULT_PORT}" in captured.out


def test_get_host_port_only_host(monkeypatch):
    """Test get_host_port when only HOST is set."""
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.setenv("HOST", "192.168.1.1")

    host, port = get_host_port()

    assert host == "192.168.1.1"
    assert port == DEFAULT_PORT


def test_get_host_port_only_port(monkeypatch):
    """Test get_host_port when only PORT is set."""
    monkeypatch.setenv("PORT", "9090")
    monkeypatch.delenv("HOST", raising=False)

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == 9090


def test_health_endpoint():
    """Test the /health endpoint of the app."""
    from html2md.app import app

    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "html2md"
    assert "version" in data
