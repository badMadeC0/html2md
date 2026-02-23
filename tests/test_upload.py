import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_upload_api_error(capsys, tmp_path):
    """Test that anthropic.APIError is caught and printed as 'Error: ...'."""

    # Mock anthropic module before importing html2md.upload
    mock_anthropic = MagicMock()

    # Mock APIError exception class
    class MockAPIError(Exception):
        pass
    mock_anthropic.APIError = MockAPIError

    # Mock Anthropic client
    mock_client_instance = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client_instance

    # Mock upload to raise APIError
    mock_client_instance.beta.files.upload.side_effect = MockAPIError("Some API error")

    # Create a dummy file for the test
    dummy_file = tmp_path / "dummy_test_upload.txt"
    dummy_file.write_text("test content")

    with patch.dict(sys.modules, {'anthropic': mock_anthropic}):
        # Import inside the patch to ensure it uses the mock
        import html2md.upload
        # Reload if already imported
        import importlib
        importlib.reload(html2md.upload)

        exit_code = html2md.upload.main([str(dummy_file)])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: Some API error" in captured.err

def test_upload_file_not_found(capsys):
    """Test that FileNotFoundError is caught and printed as 'Error: ...'."""

    mock_anthropic = MagicMock()

    with patch.dict(sys.modules, {'anthropic': mock_anthropic}):
        import html2md.upload
        import importlib
        importlib.reload(html2md.upload)

        exit_code = html2md.upload.main(["non_existent_file.txt"])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: File not found: non_existent_file.txt" in captured.err
