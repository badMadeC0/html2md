import os
from unittest.mock import patch

import pytest

from html2md.config import DEFAULT_PORT, get_host_port


class TestGetHostPort:
    def test_default_values(self):
        """Test default values when no environment variables are set."""
        with patch.dict(os.environ, {}, clear=True):
            host, port = get_host_port()
            assert host == "0.0.0.0"
            assert port == DEFAULT_PORT

    def test_custom_port_valid(self):
        """Test valid custom port from environment variable."""
        with patch.dict(os.environ, {"PORT": "8080"}, clear=True):
            host, port = get_host_port()
            assert port == 8080

    def test_custom_port_invalid(self, capsys):
        """Test invalid custom port from environment variable fallback to default."""
        with patch.dict(os.environ, {"PORT": "invalid_port"}, clear=True):
            host, port = get_host_port()
            assert port == DEFAULT_PORT

            # Check warning message
            captured = capsys.readouterr()
            assert (
                f"Warning: Invalid PORT environment variable value 'invalid_port'; falling back to default {DEFAULT_PORT}."
                in captured.out
            )

    def test_custom_host(self):
        """Test valid custom host from environment variable."""
        with patch.dict(os.environ, {"HOST": "127.0.0.1"}, clear=True):
            host, port = get_host_port()
            assert host == "127.0.0.1"

    def test_custom_host_and_port(self):
        """Test valid custom host and port from environment variables."""
        with patch.dict(
            os.environ, {"HOST": "192.168.1.1", "PORT": "9090"}, clear=True
        ):
            host, port = get_host_port()
            assert host == "192.168.1.1"
            assert port == 9090
