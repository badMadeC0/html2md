import pytest

# Skip this entire module if flask is not installed
flask = pytest.importorskip("flask")

from html2md import __version__
from html2md.app import app

@pytest.fixture
def client():
    """A test client for the app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert data["status"] == "ok"
    assert data["service"] == "html2md"
    assert data["version"] == __version__
