from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock flask so we can test app.py functions even if flask is not installed
sys.modules["flask"] = MagicMock()

from html2md.app import DEFAULT_PORT, get_host_port


def test_get_host_port_defaults() -> None:
    """Test get_host_port returns defaults when environment is empty."""
    with patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT


def test_get_host_port_valid_port() -> None:
    """Test get_host_port parses a valid PORT environment variable."""
    with patch.dict(os.environ, {"PORT": "8080"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == 8080


def test_get_host_port_invalid_port(capsys: pytest.CaptureFixture[str]) -> None:
    """Test get_host_port falls back to default and warns on invalid PORT."""
    with patch.dict(os.environ, {"PORT": "not_a_number"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert "Warning: Invalid PORT environment variable value" in captured.out
        assert "'not_a_number'" in captured.out


def test_get_host_port_custom_host() -> None:
    """Test get_host_port parses a custom HOST environment variable."""
    with patch.dict(os.environ, {"HOST": "127.0.0.1"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == DEFAULT_PORT


def test_get_host_port_custom_host_and_port() -> None:
    """Test get_host_port parses custom HOST and PORT environment variables."""
    with patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "9090"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == 9090
