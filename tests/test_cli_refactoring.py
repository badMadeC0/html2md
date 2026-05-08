"""Tests for html2md CLI refactoring helpers."""

import builtins
import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from html2md.cli import DependencyError, load_dependencies, setup_session


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
