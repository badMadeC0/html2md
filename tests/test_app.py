import pytest

# Skip this entire module if flask is not installed
pytest.importorskip("flask")

from html2md import __version__
from html2md.app import app


@pytest.fixture
def client():
    """A test client for the app."""
    original_testing = app.config.get("TESTING", False)
    app.config["TESTING"] = True
    try:
        with app.test_client() as client:
            yield client
    finally:
        app.config["TESTING"] = original_testing


def test_health(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

    assert response.get_json() == {
        "status": "ok",
        "service": "html2md",
        "version": __version__,
    }
