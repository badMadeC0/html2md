"""Tests for the Flask application."""

import pytest

try:
    import flask
except ImportError:
    flask = None


@pytest.mark.skipif(flask is None, reason="Flask is not installed")
def test_health():
    """Test the health endpoint."""
    from html2md.app import app
    from html2md import __version__

    with app.test_client() as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "html2md"
        assert data["version"] == __version__
