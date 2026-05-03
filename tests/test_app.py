import os
import pytest

# Skip the test module if flask is not installed.
pytest.importorskip("flask")

from html2md.app import get_host_port

def test_get_host_port_default(monkeypatch):
    """Test get_host_port returns default localhost when HOST is not set."""
    # Ensure HOST and PORT are not set in the environment
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)

    hostname, port = get_host_port()
    assert hostname == "127.0.0.1"
    assert port == 10000

def test_get_host_port_custom_host(monkeypatch):
    """Test get_host_port respects the HOST environment variable."""
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.delenv("PORT", raising=False)

    hostname, port = get_host_port()
    assert hostname == "0.0.0.0"
    assert port == 10000

def test_get_host_port_custom_port(monkeypatch):
    """Test get_host_port respects the PORT environment variable."""
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.setenv("PORT", "8080")

    hostname, port = get_host_port()
    assert hostname == "127.0.0.1"
    assert port == 8080
