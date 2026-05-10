"""Tests for the Flask application endpoints."""

import pytest

pytest.importorskip("flask")

from html2md import __version__
from html2md.app import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setitem(app.config, "TESTING", True)
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the /health endpoint returns the expected status and version."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data == {'status': 'ok', 'service': 'html2md', 'version': __version__}
