"""Tests for SSRF protection."""

import sys
import os
import socket
import logging
from unittest.mock import MagicMock, patch
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from html2md.cli import main

@pytest.fixture
def mock_deps():
    """Mock requests and markdownify modules."""
    with patch.dict(sys.modules, {'requests': MagicMock(), 'markdownify': MagicMock()}):
        yield sys.modules['requests'], sys.modules['markdownify']

def test_private_ip_blocked(mock_deps, caplog):
    mock_requests, _ = mock_deps
    caplog.set_level(logging.INFO)

    # Run with private IP
    main(['--url', 'http://192.168.1.1'])

    assert "Blocked private IP: 192.168.1.1" in caplog.text

    # Verify get was not called
    session = mock_requests.Session.return_value
    assert not session.get.called

def test_dns_rebinding_prevention(mock_deps, caplog):
    mock_requests, _ = mock_deps
    caplog.set_level(logging.INFO)

    # Mock socket.getaddrinfo to return private IP for a domain
    with patch('socket.getaddrinfo') as mock_dns:
        # family, type, proto, canonname, sockaddr
        mock_dns.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 80))]

        main(['--url', 'http://malicious.com'])

        assert "Blocked domain resolving to private IP" in caplog.text
        session = mock_requests.Session.return_value
        assert not session.get.called

def test_safe_url_allowed(mock_deps, caplog):
    mock_requests, mock_md = mock_deps
    caplog.set_level(logging.INFO)

    with patch('socket.getaddrinfo') as mock_dns:
        mock_dns.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 80))]

        session = mock_requests.Session.return_value
        response = session.get.return_value
        response.is_redirect = False
        response.text = "<html><body>Hello</body></html>"

        main(['--url', 'http://google.com'])

        assert "Fetching content from: http://google.com" in caplog.text
        session.get.assert_called_with('http://google.com', timeout=30, allow_redirects=False)

def test_redirect_handling(mock_deps, caplog):
    mock_requests, _ = mock_deps
    caplog.set_level(logging.INFO)

    with patch('socket.getaddrinfo') as mock_dns:
        mock_dns.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 80))]

        session = mock_requests.Session.return_value

        # Setup responses
        resp1 = MagicMock()
        resp1.is_redirect = True
        resp1.headers = {'Location': 'http://google.com/final'}

        resp2 = MagicMock()
        resp2.is_redirect = False
        resp2.text = "Content"

        session.get.side_effect = [resp1, resp2]

        main(['--url', 'http://google.com'])

        # Should see redirect
        assert "Redirecting: http://google.com -> http://google.com/final" in caplog.text
        # Verify calls
        # 1. http://google.com
        # 2. http://google.com/final
        assert session.get.call_count == 2

def test_redirect_to_private_blocked(mock_deps, caplog):
    mock_requests, _ = mock_deps
    caplog.set_level(logging.INFO)

    # We need separate behaviors for getaddrinfo depending on the host
    def side_effect(host, port, family=0, type=0, proto=0, flags=0):
        if host == 'google.com':
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 80))]
        elif host == 'private.com':
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.168.1.1', 80))]
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 80))]

    with patch('socket.getaddrinfo', side_effect=side_effect):
        session = mock_requests.Session.return_value

        # First request redirects to private domain
        resp1 = MagicMock()
        resp1.is_redirect = True
        resp1.headers = {'Location': 'http://private.com'}

        session.get.side_effect = [resp1]

        main(['--url', 'http://google.com'])

        assert "Redirecting: http://google.com -> http://private.com" in caplog.text
        assert "Blocked domain resolving to private IP: private.com" in caplog.text

        # Should only have called get once (initial)
        assert session.get.call_count == 1
