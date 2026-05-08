from html2md.server_config import DEFAULT_HOST, DEFAULT_PORT, get_host_port


def test_get_host_port_default(monkeypatch):
    """Test get_host_port returns default localhost when HOST is not set."""
    # Ensure HOST and PORT are not set in the environment
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)

    hostname, port = get_host_port()
    assert hostname == DEFAULT_HOST
    assert port == DEFAULT_PORT


def test_get_host_port_custom_host(monkeypatch):
    """Test get_host_port respects the HOST environment variable."""
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.delenv("PORT", raising=False)

    hostname, port = get_host_port()
    assert hostname == "0.0.0.0"
    assert port == DEFAULT_PORT


def test_get_host_port_empty_host(monkeypatch):
    """Test get_host_port falls back to localhost when HOST is empty."""
    monkeypatch.setenv("HOST", "")
    monkeypatch.delenv("PORT", raising=False)

    hostname, port = get_host_port()
    assert hostname == DEFAULT_HOST
    assert port == DEFAULT_PORT


def test_get_host_port_custom_port(monkeypatch):
    """Test get_host_port respects the PORT environment variable."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.setenv("PORT", "8080")

    hostname, port = get_host_port()
    assert hostname == DEFAULT_HOST
    assert port == 8080
