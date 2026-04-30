import os
import pytest
from unittest.mock import patch

pytest.importorskip("flask")

from html2md.app import validate_port, get_host_port, DEFAULT_PORT


def test_validate_port_valid():
    """Test validate_port with valid inputs."""
    assert validate_port(1) == 1
    assert validate_port(65535) == 65535
    assert validate_port(8080) == 8080
    assert validate_port("3000") == 3000


def test_validate_port_invalid():
    """Test validate_port with out of bounds values."""
    with pytest.raises(ValueError):
        validate_port(0)

    with pytest.raises(ValueError):
        validate_port(65536)

    with pytest.raises(ValueError):
        validate_port(-1)


def test_validate_port_non_numeric():
    """Test validate_port with non-numeric values."""
    with pytest.raises(ValueError):
        validate_port("abc")

    with pytest.raises(ValueError):
        validate_port("")


def test_get_host_port_defaults():
    """Test get_host_port without environment variables."""
    with patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT


def test_get_host_port_custom():
    """Test get_host_port with valid environment variables."""
    with patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "8080"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == 8080


def test_get_host_port_invalid_port(capsys):
    """Test get_host_port with invalid PORT value."""
    with patch.dict(os.environ, {"HOST": "192.168.1.1", "PORT": "invalid"}, clear=True):
        host, port = get_host_port()
        assert host == "192.168.1.1"
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'invalid'" in captured.out


def test_get_host_port_out_of_bounds_port(capsys):
    """Test get_host_port with out of bounds PORT value."""
    with patch.dict(os.environ, {"PORT": "70000"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'70000'" in captured.out
