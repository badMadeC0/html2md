import os
import pytest
from html2md.app import app, get_host_port

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_default_host(monkeypatch):
    monkeypatch.delenv('HOST', raising=False)
    host, port = get_host_port()
    assert host == '127.0.0.1'

def test_security_headers(client):
    response = client.get('/health')
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert 'Strict-Transport-Security' in response.headers
