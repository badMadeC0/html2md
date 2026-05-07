"""Tests for the Flask application endpoints."""

import pytest

from html2md import __version__
from html2md.app import app


@pytest.fixture
def client():
    missing = object()
    old_testing = app.config.get('TESTING', missing)
    app.config['TESTING'] = True
    try:
        with app.test_client() as client:
            yield client
    finally:
        if old_testing is missing:
            app.config.pop('TESTING', None)
        else:
            app.config['TESTING'] = old_testing


def test_health_endpoint(client):
    """Test the /health endpoint returns the expected status and version."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data == {'status': 'ok', 'service': 'html2md', 'version': __version__}
