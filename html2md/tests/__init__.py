"""Test suite for html2md."""

import requests  # type: ignore

def test_requests() -> None:
    """Test requests import."""
    if requests is None:
        return
    assert requests is not None
