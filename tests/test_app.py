import os
from unittest.mock import patch
import pytest

pytest.importorskip("flask")

from html2md.app import get_host_port, DEFAULT_PORT


def test_get_host_port_defaults():
    with patch.dict(os.environ, {}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT


def test_get_host_port_custom_port():
    with patch.dict(os.environ, {"PORT": "8080"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == 8080


def test_get_host_port_custom_host():
    with patch.dict(os.environ, {"HOST": "127.0.0.1"}, clear=True):
        host, port = get_host_port()
        assert host == "127.0.0.1"
        assert port == DEFAULT_PORT


def test_get_host_port_invalid_port(capsys):
    with patch.dict(os.environ, {"PORT": "invalid"}, clear=True):
        host, port = get_host_port()
        assert host == "0.0.0.0"
        assert port == DEFAULT_PORT

        captured = capsys.readouterr()
        assert (
            "Warning: Invalid PORT environment variable value 'invalid'" in captured.out
        )
