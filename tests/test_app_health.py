import os
import pytest
from flask import Flask
from html2md.app import app, get_host_port, DEFAULT_PORT


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["status"] == "ok"
    assert json_data["service"] == "html2md"


def test_get_host_port_defaults(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HOST", raising=False)
    host, port = get_host_port()
    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT


def test_get_host_port_custom(monkeypatch):
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("HOST", "127.0.0.1")
    host, port = get_host_port()
    assert host == "127.0.0.1"
    assert port == 8080


def test_get_host_port_invalid_port(monkeypatch, capsys):
    monkeypatch.setenv("PORT", "not_a_number")
    host, port = get_host_port()
    assert port == DEFAULT_PORT
    captured = capsys.readouterr()
    assert "Invalid PORT environment variable value" in captured.out
    assert str(DEFAULT_PORT) in captured.out
