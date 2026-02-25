"""Test suite for html2md."""

import pytest


def test_requests() -> None:
    """Test requests import."""
    requests = pytest.importorskip("requests")
    assert requests is not None
