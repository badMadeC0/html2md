"""Test suite for html2md."""

import requests  # type: ignore


def test_requests() -> None:
    """Test requests import."""
    assert requests is not None
