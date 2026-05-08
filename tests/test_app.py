"""Tests for the Flask application."""

import pytest

pytest.importorskip("flask")

from html2md import __version__
from html2md.app import DEFAULT_HOST, DEFAULT_PORT, app, get_host_port


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
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


@pytest.mark.parametrize(
    ("env", "expected_host", "expected_port", "expected_warning"),
    [
        ({}, DEFAULT_HOST, DEFAULT_PORT, None),
        ({"HOST": "127.0.0.1", "PORT": "8080"}, "127.0.0.1", 8080, None),
        (
            {"PORT": "not-a-number"},
            DEFAULT_HOST,
            DEFAULT_PORT,
            "Invalid PORT environment variable value 'not-a-number'",
        ),
    ],
)
def test_get_host_port(monkeypatch, capsys, env, expected_host, expected_port, expected_warning):
    """Test get_host_port across environment variable scenarios."""
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HOST", raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    host, port = get_host_port()

    assert host == expected_host
    assert port == expected_port

    captured = capsys.readouterr()
    if expected_warning is None:
        assert captured.out == ""
    else:
        assert expected_warning in captured.out
