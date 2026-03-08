"""Test suite for html2md."""

import pytest
pytest.importorskip('requests')
import requests

def test_requests() -> None:
    """Test requests import."""
    assert requests is not None
