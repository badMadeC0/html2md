import os
import sys
from unittest.mock import MagicMock, patch
import tempfile
import shutil

import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from html2md.cli import main


@pytest.fixture
def temp_dir():
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def test_markdownify_strip_arguments(temp_dir):
    # Create mocks
    mock_requests = MagicMock()
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '<html><script>alert(1)</script></html>'
    mock_response.raise_for_status.return_value = None
    mock_session.get.return_value = mock_response
    mock_requests.Session.return_value = mock_session

    mock_markdownify_module = MagicMock()
    mock_md = MagicMock()
    mock_md.return_value = "converted content"
    mock_markdownify_module.markdownify = mock_md

    # Patch sys.modules to inject mocks
    # We need to patch 'requests' and 'markdownify' so that the imports inside main() pick them up
    with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify_module}):
        # Run CLI
        url = 'http://example.com/test'
        argv = ['--url', url, '--outdir', temp_dir]

        ret = main(argv)

        assert ret == 0, "CLI returned non-zero exit code"

        # Verify markdownify was called with strip argument
        args, kwargs = mock_md.call_args
        assert args[0] == mock_response.text
        assert kwargs.get('heading_style') == 'ATX'

        # The crucial check:
        strip_arg = kwargs.get('strip')

        assert strip_arg is not None, "markdownify called without 'strip' argument"
        # Explicitly define the list of tags to check for, to match what's in the CLI code
        STRIP_TAGS = ['script', 'style', 'iframe', 'object', 'embed', 'link', 'meta']
        for tag in STRIP_TAGS:
       	    assert tag in strip_arg, f"Tag '{tag}' not found in strip argument"
