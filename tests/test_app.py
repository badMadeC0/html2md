import os
from unittest.mock import patch

from html2md.app import DEFAULT_PORT, app, get_host_port


def test_health():
    with app.test_client() as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "html2md"


def test_get_host_port_defaults():
    with patch.dict(os.environ, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == 10000


def test_get_host_port_env_vars():
    with patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "8080"}):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == 8080


def test_get_host_port_invalid_port():
    with patch.dict(os.environ, {"PORT": "invalid"}):
        host, port = get_host_port()
        assert port == 10000
