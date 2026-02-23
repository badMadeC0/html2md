import sys
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_upload_module():
    """Fixture that mocks anthropic module and imports html2md.upload."""
    mock_anthropic = MagicMock()

    class MockAPIError(Exception):
        def __init__(self, message, request=None, body=None):
            super().__init__(message)
            self.message = message
            self.request = request
            self.body = body

    mock_anthropic.APIError = MockAPIError
    mock_anthropic.Anthropic = MagicMock()

    original_upload_module = sys.modules.pop('html2md.upload', None)
    try:
        with patch.dict(sys.modules, {'anthropic': mock_anthropic}):
            import html2md.upload
            yield html2md.upload
    finally:
        # Cleanup: remove the mocked module and restore original if it existed
        if 'html2md.upload' in sys.modules:
            del sys.modules['html2md.upload']
        if original_upload_module:
            sys.modules['html2md.upload'] = original_upload_module

def test_upload_main_api_error(mock_upload_module, capsys):
    upload = mock_upload_module
    mock_anthropic = sys.modules['anthropic']
    MockAPIError = mock_anthropic.APIError

    with patch('html2md.upload.upload_file') as mock_upload:
        mock_upload.side_effect = MockAPIError("Test API Error")
        ret = upload.main(['dummy.txt'])
        assert ret == 1
        captured = capsys.readouterr()
        assert "API error: Test API Error" in captured.err

def test_upload_main_file_not_found(mock_upload_module, capsys):
    upload = mock_upload_module
    with patch('html2md.upload.upload_file') as mock_upload:
        mock_upload.side_effect = FileNotFoundError("File not found")
        ret = upload.main(['nonexistent.txt'])
        assert ret == 1
        captured = capsys.readouterr()
        assert "Error: File not found" in captured.err

def test_upload_main_success(mock_upload_module, capsys):
    upload = mock_upload_module
    with patch('html2md.upload.upload_file') as mock_upload:
        mock_result = MagicMock()
        mock_result.id = "file_12345"
        mock_upload.return_value = mock_result
        ret = upload.main(['valid.txt'])
        assert ret == 0
        captured = capsys.readouterr()
        assert "File uploaded successfully. ID: file_12345" in captured.out

def test_upload_file_success(mock_upload_module, tmp_path):
    upload = mock_upload_module
    test_file = tmp_path / "test.txt"
    test_file.write_text("content", encoding='utf-8')

    # We need to mock Anthropic inside the imported module
    mock_anthropic = sys.modules['anthropic']

    mock_client = mock_anthropic.Anthropic.return_value
    mock_files = mock_client.beta.files
    mock_upload_resp = MagicMock()
    mock_upload_resp.id = "file_abc"
    mock_files.upload.return_value = mock_upload_resp

    result = upload.upload_file(str(test_file))

    assert result.id == "file_abc"
    mock_files.upload.assert_called_once()

    call_args = mock_files.upload.call_args
    kwargs = call_args.kwargs
    assert 'file' in kwargs
    file_arg = kwargs['file']
    assert isinstance(file_arg, tuple)
    assert len(file_arg) == 3
    # Verify filename, file handle, and MIME type
    assert file_arg[0] == "test.txt"
    assert hasattr(file_arg[1], "read")
    assert file_arg[2] == "text/plain"

def test_upload_file_not_found(mock_upload_module):
    upload = mock_upload_module
    with pytest.raises(FileNotFoundError):
        upload.upload_file("non_existent_file.txt")
