"""Tests for html2md CLI refactoring helpers."""

import builtins
import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from html2md.cli import DependencyError, load_dependencies, process_url, setup_session


def test_load_dependencies_success(monkeypatch):
    """Test loading dependencies works when available."""
    fake_requests = ModuleType("requests")
    fake_markdownify = ModuleType("markdownify")

    def fake_md(*args, **kwargs):
        return "markdown"

    fake_markdownify.markdownify = fake_md
    monkeypatch.setitem(sys.modules, "requests", fake_requests)
    monkeypatch.setitem(sys.modules, "markdownify", fake_markdownify)

    requests_module, md_func = load_dependencies()

    assert requests_module is fake_requests
    assert md_func is fake_md


def test_load_dependencies_failure(monkeypatch):
    """Test load_dependencies raises DependencyError on import failure."""

    class MockImportError(ImportError):
        """ImportError carrying the missing dependency name."""

        def __init__(self, message, name):
            super().__init__(message)
            self.name = name

    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "requests":
            raise MockImportError("mock error", "requests")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    with pytest.raises(DependencyError, match="Missing dependency requests"):
        load_dependencies()


def test_load_dependencies_failure_without_name_uses_message(monkeypatch):
    """Test dependency errors use a fallback when ImportError.name is empty."""

    class NamelessImportError(ImportError):
        """ImportError test double with no dependency name."""

        def __init__(self, message):
            super().__init__(message)
            self.name = None

    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "requests":
            raise NamelessImportError("manual import failure")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

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

    assert session is mock_session_obj
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
