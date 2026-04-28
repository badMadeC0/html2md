"""Tests for the flask app."""

import pytest

flask = pytest.importorskip("flask")

from html2md import __version__
from html2md.app import app


@pytest.fixture
def client():
    """Create a Flask test client for the app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_get(client):
    """Test that the health endpoint returns a valid response."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert data["status"] == "ok"
    assert data["service"] == "html2md"
    assert data["version"] == __version__


def test_health_post_not_allowed(client):
    """Test that POST to health endpoint is not allowed."""
    response = client.post("/health")
    assert response.status_code == 405
