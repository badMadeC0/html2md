import importlib
import os
from unittest.mock import patch

import pytest


try:
    importlib.import_module("flask")
except ModuleNotFoundError as exc:
    if exc.name == "flask":
        pytest.skip(
            "could not import 'flask': No module named 'flask'",
            allow_module_level=True,
        )
    raise

from html2md.app import DEFAULT_PORT, app, get_host_port


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "html2md"
    assert "version" in data


@patch.dict(os.environ, {}, clear=True)
def test_get_host_port_defaults():
    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT


@patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "8080"}, clear=True)
def test_get_host_port_custom():
    host, port = get_host_port()
    assert host == "127.0.0.1"
    assert port == 8080


@patch.dict(os.environ, {"PORT": "invalid"}, clear=True)
def test_get_host_port_invalid_port(capsys):
    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT

    captured = capsys.readouterr()
    assert "Warning: Invalid PORT environment variable value" in captured.out
    assert "'invalid'" in captured.out
