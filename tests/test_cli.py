import os
import sys
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from html2md.cli import main

def test_batch_file_not_found():
    result = main(['--batch', 'nonexistent_file.txt'])
    assert result == 1

def test_batch_success():
    # Create temp batch file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("http://example.com/1\n")
        f.write("http://example.com/2\n")
        f.write(" \n") # empty line
        f.write("http://example.com/3/?\n") # test url formatting fix
        batch_file = f.name

    try:
        # We must use sys.modules patching because the modules are imported inside main()
        # and aren't accessible via html2md.cli.requests or html2md.cli.markdownify
        # AND we don't have them installed in our test environment
        mock_requests = MagicMock()
        mock_session_instance = MagicMock()
        mock_requests.Session.return_value = mock_session_instance

        mock_response = MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_session_instance.get.return_value = mock_response

        mock_markdownify = MagicMock()
        mock_markdownify.markdownify.return_value = "# Test"

        with patch.dict('sys.modules', {'requests': mock_requests, 'markdownify': mock_markdownify}):
            # Capture stdout to avoid printing during tests
            with patch('builtins.print'):
                result = main(['--batch', batch_file])

        assert result == 0
        assert mock_session_instance.get.call_count == 3
        mock_session_instance.get.assert_any_call("http://example.com/1", timeout=30)
        mock_session_instance.get.assert_any_call("http://example.com/2", timeout=30)
        mock_session_instance.get.assert_any_call("http://example.com/3?", timeout=30)
        assert mock_markdownify.markdownify.call_count == 3
    finally:
        os.unlink(batch_file)

def test_batch_success_with_outdir():
    # Create temp directory and batch file
    with tempfile.TemporaryDirectory() as temp_dir:
        batch_file = os.path.join(temp_dir, 'urls.txt')
        out_dir = os.path.join(temp_dir, 'out')

        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write("http://example.com/page1\n")
            f.write("http://example.com/page2\n")

        mock_requests = MagicMock()
        mock_session_instance = MagicMock()
        mock_requests.Session.return_value = mock_session_instance

        mock_response = MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_session_instance.get.return_value = mock_response

        mock_markdownify = MagicMock()
        mock_markdownify.markdownify.return_value = "# Test"

        with patch.dict('sys.modules', {'requests': mock_requests, 'markdownify': mock_markdownify}):
            # Run command
            with patch('builtins.print'):
                result = main(['--batch', batch_file, '--outdir', out_dir])

        assert result == 0
        assert mock_session_instance.get.call_count == 2

        # Check files were created
        assert os.path.exists(out_dir)

        file1_path = os.path.join(out_dir, 'page1.md')
        file2_path = os.path.join(out_dir, 'page2.md')

        assert os.path.exists(file1_path)
        assert os.path.exists(file2_path)

        with open(file1_path, 'r', encoding='utf-8') as f:
            assert f.read() == "# Test"

        with open(file2_path, 'r', encoding='utf-8') as f:
            assert f.read() == "# Test"

def test_batch_exception_handling():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("http://example.com/fail\n")
        f.write("http://example.com/success\n")
        batch_file = f.name

    try:
        mock_requests = MagicMock()

        # Setup real-ish exception class
        class FakeRequestException(Exception): pass
        mock_requests.exceptions.RequestException = FakeRequestException

        mock_session_instance = MagicMock()
        mock_requests.Session.return_value = mock_session_instance

        def side_effect(url, **kwargs):
            if url == "http://example.com/fail":
                raise FakeRequestException("Network error")

            mock_response = MagicMock()
            mock_response.text = "<html><body>Test</body></html>"
            return mock_response

        mock_session_instance.get.side_effect = side_effect

        mock_markdownify = MagicMock()
        mock_markdownify.markdownify.return_value = "# Test"

        with patch.dict('sys.modules', {'requests': mock_requests, 'markdownify': mock_markdownify}):
            with patch('builtins.print') as mock_print:
                result = main(['--batch', batch_file])

        assert result == 0
        assert mock_session_instance.get.call_count == 2
        # Check that the exception was caught and printed, and we continued to the next URL
        assert any("Conversion failed" in call[0][0] for call in mock_print.call_args_list)
        mock_session_instance.get.assert_any_call("http://example.com/success", timeout=30)
    finally:
        os.unlink(batch_file)
