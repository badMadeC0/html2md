"""Tests for the flask app."""

from importlib.util import find_spec
from unittest.mock import patch

import pytest

from html2md import __version__

HAS_FLASK = find_spec("flask") is not None
pytestmark = pytest.mark.skipif(
    not HAS_FLASK,
    reason="Flask is not installed; install the deploy extra to run app tests",
)

if HAS_FLASK:
    from html2md.app import app
else:
    app = None


@pytest.fixture
def client():
    """Create a Flask test client for the app."""
    with patch.dict(app.config, {"TESTING": True}):
        with app.test_client() as client:
            yield client


def test_health_get(client):
    """Test that the health endpoint returns a valid response."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.mimetype == "application/json"

    data = response.get_json()
    assert data is not None
    assert data["status"] == "ok"
    assert data["service"] == "html2md"
    assert data["version"] == __version__


def test_health_post_not_allowed(client):
    """Test that POST to health endpoint is not allowed."""
    response = client.post("/health")
    assert response.status_code == 405
