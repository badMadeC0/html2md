"""Tests for the Flask application entry point configuration."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

pytest.importorskip('flask')

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from html2md.app import (  # noqa: E402
    DEFAULT_PORT,
    DEPLOY_HOST,
    LOCAL_HOST,
    get_host_port,
)


def test_get_host_port_defaults_to_localhost_for_local_runs():
    """Direct local runs without platform env vars should stay loopback-only."""
    with patch.dict(os.environ, {}, clear=True):
        assert get_host_port() == (LOCAL_HOST, DEFAULT_PORT)


def test_get_host_port_uses_deploy_host_when_platform_port_is_set():
    """PaaS/container runs with only PORT should remain externally reachable."""
    with patch.dict(os.environ, {'PORT': '8080'}, clear=True):
        assert get_host_port() == (DEPLOY_HOST, 8080)


def test_get_host_port_honors_explicit_host_over_platform_default():
    """An explicit HOST should override both local and deploy defaults."""
    with patch.dict(os.environ, {'HOST': '127.0.0.1', 'PORT': '8080'}, clear=True):
        assert get_host_port() == (LOCAL_HOST, 8080)
