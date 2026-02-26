from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def cli_mocks():
    """Fixture to set up common mocks for CLI tests."""
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session

    mock_requests_exceptions = MagicMock()
    mock_requests_exceptions.RequestException = type("RequestException", (Exception,), {})
    mock_requests.exceptions = mock_requests_exceptions

    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_session.get.return_value = mock_response

    mock_markdownify.markdownify.return_value = "Markdown Content"

    with patch.dict(
        sys.modules,
        {
            "requests": mock_requests,
            "requests.exceptions": mock_requests_exceptions,
            "markdownify": mock_markdownify,
            "bs4": mock_bs4,
            "reportlab.platypus": mock_reportlab_platypus,
            "reportlab.lib.styles": mock_reportlab_styles,
        },
    ):
        yield {
            "requests": mock_requests,
            "session": mock_session,
            "requests_exceptions": mock_requests_exceptions,
            "markdownify": mock_markdownify,
            "bs4": mock_bs4,
            "reportlab_platypus": mock_reportlab_platypus,
            "reportlab_lib_styles": mock_reportlab_styles,
            "response": mock_response,
        }
