"""Test suite for html2md."""

try:
    import requests  # type: ignore
except ImportError:
    requests = None

def test_requests() -> None:
    """Test requests import."""
    if requests is None:
        return
    assert requests is not None
