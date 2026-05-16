import os
import pytest
from unittest.mock import patch

flask = pytest.importorskip("flask")

from html2md.app import get_host_port, app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "html2md"


def test_get_host_port_default_values():
    with patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == 10000


def test_get_host_port_custom_values():
    with patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "8080"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == 8080


def test_get_host_port_invalid_port_fallback(capsys):
    with patch.dict(os.environ, {"PORT": "not-a-number"}, clear=True):
        host, port = get_host_port()

        # Check return values
        assert host == "0.0.0.0"
        assert port == 10000

        # Check printed warning
        captured = capsys.readouterr()
        assert (
            "Warning: Invalid PORT environment variable value 'not-a-number'; falling back to default 10000."
            in captured.out
        )
