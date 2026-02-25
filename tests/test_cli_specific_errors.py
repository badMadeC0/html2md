import logging
import sys
import os
from unittest.mock import MagicMock, patch

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli

# Helper to setup mocks with exception class
def setup_mocks():
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    class MockRequestException(Exception):
        pass

    mock_requests.RequestException = MockRequestException
    mock_requests.exceptions.RequestException = MockRequestException

    return mock_requests, mock_markdownify, mock_bs4, mock_reportlab_platypus, mock_reportlab_styles, MockRequestException

def test_cli_conversion_request_exception(capsys, caplog):
    mock_requests, mock_markdownify, mock_bs4, mock_reportlab_platypus, mock_reportlab_styles, MockRequestException = setup_mocks()

    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_session.get.side_effect = MockRequestException('Connection refused')

    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
            html2md.cli.main(['--url', 'http://example.com'])

    assert 'Network error: Connection refused' in caplog.text
    assert 'Conversion failed' not in caplog.text

def test_cli_conversion_os_error(capsys, caplog):
    # Even though we raise OSError, we must ensure requests.RequestException is a valid class
    # because python evaluates except clauses.
    mock_requests, mock_markdownify, mock_bs4, mock_reportlab_platypus, mock_reportlab_styles, _ = setup_mocks()

    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_session.get.side_effect = OSError('Disk full')

    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
            html2md.cli.main(['--url', 'http://example.com'])

    assert 'File error: Disk full' in caplog.text
    assert 'Conversion failed' not in caplog.text
