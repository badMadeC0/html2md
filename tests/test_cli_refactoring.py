"""Tests for extracted CLI helper functions."""

from unittest.mock import MagicMock, patch

import pytest

from html2md.cli import DependencyError, load_dependencies, process_url, setup_session


class MockImportError(ImportError):
    """ImportError test double with a configurable missing dependency name."""

    def __init__(self, message, name):
        super().__init__(message)
        self.name = name


def test_load_dependencies_success():
    """Test loading dependencies works when available."""
    requests_module, md_func = load_dependencies()
    assert requests_module is not None
    assert md_func is not None
    assert callable(md_func)


@patch("builtins.__import__")
def test_load_dependencies_failure(mock_import):
    """Test load_dependencies raises DependencyError on failure."""
    mock_import.side_effect = MockImportError("mock error", "requests")

    with pytest.raises(DependencyError, match="Missing dependency requests"):
        load_dependencies()


@patch("builtins.__import__")
def test_load_dependencies_failure_without_name_uses_message(mock_import):
    """Test dependency errors use a fallback when ImportError.name is empty."""
    mock_import.side_effect = MockImportError("manual import failure", None)

    expected_message = "Missing dependency manual import failure"
    with pytest.raises(DependencyError, match=expected_message):
        load_dependencies()


def test_setup_session():
    """Test setup_session configures default headers correctly."""
    mock_requests = MagicMock()
    mock_session_obj = MagicMock()
    mock_requests.Session.return_value = mock_session_obj
    mock_session_obj.headers = {}

    session = setup_session(mock_requests)

    assert session == mock_session_obj
    assert "User-Agent" in session.headers
    assert "Accept" in session.headers


def test_process_url_catches_injected_request_exception(capsys):
    """Test process_url catches network errors from the injected requests module."""

    class InjectedRequestException(Exception):
        """Network exception from an injected requests-compatible module."""

    fake_requests = MagicMock()
    fake_requests.RequestException = InjectedRequestException
    fake_session = MagicMock()
    fake_session.get.side_effect = InjectedRequestException("injected network error")
    md_func = MagicMock()

    process_url("https://example.com", fake_session, md_func, None, fake_requests)

    outerr = capsys.readouterr()
    assert "Network error: injected network error" in outerr.err
    md_func.assert_not_called()
