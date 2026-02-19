"""Tests for html2md.upload."""
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock anthropic before importing html2md.upload as it is not installed in the environment
# This is required for the import to succeed.
if "anthropic" not in sys.modules:
    sys.modules["anthropic"] = MagicMock()

from html2md.upload import upload_file, main

"""Tests for html2md.upload."""
import sys
from unittest.mock import MagicMock
import pytest

# Mock anthropic before importing html2md.upload as it is not installed in the environment
# This is required for the import to succeed.
if "anthropic" not in sys.modules:
    sys.modules["anthropic"] = MagicMock()

from html2md.upload import upload_file, main

def test_upload_file_no_client(mocker):
    """Test upload_file creates a new client when none is provided."""
    mock_anthropic = mocker.patch("html2md.upload.anthropic")
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    # Mock path existence and open
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.open", MagicMock())

    upload_file("dummy.txt")

    mock_anthropic.Anthropic.assert_called_once()
    mock_client.beta.files.upload.assert_called_once()

def test_upload_file_with_client(mocker):
    """Test upload_file reuses the provided client."""
    mock_anthropic = mocker.patch("html2md.upload.anthropic")
    mock_client = MagicMock()

    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.open", MagicMock())

    upload_file("dummy.txt", client=mock_client)

    mock_anthropic.Anthropic.assert_not_called()
    mock_client.beta.files.upload.assert_called_once()

def test_main_passes_client(mocker):
    """Test that main creates and passes a client to upload_file."""
    mock_anthropic = mocker.patch("html2md.upload.anthropic")
    mock_upload_file = mocker.patch("html2md.upload.upload_file")
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    # Mock argv
    argv = ["dummy.txt"]

    mocker.patch("sys.stdout", new_callable=MagicMock)

    main(argv)

    mock_anthropic.Anthropic.assert_called_once()
    mock_upload_file.assert_called_once_with("dummy.txt", client=mock_client)
    """Test the upload module."""

    @patch("html2md.upload.anthropic")
    def test_upload_file_no_client(self, mock_anthropic):
        """Test upload_file creates a new client when none is provided."""
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        # Mock path existence and open
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.open", MagicMock()):

            upload_file("dummy.txt")

            mock_anthropic.Anthropic.assert_called_once()
            mock_client.beta.files.upload.assert_called_once()

    @patch("html2md.upload.anthropic")
    def test_upload_file_with_client(self, mock_anthropic):
        """Test upload_file reuses the provided client."""
        mock_client = MagicMock()

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.open", MagicMock()),
        ):

            upload_file("dummy.txt", client=mock_client)

            mock_anthropic.Anthropic.assert_not_called()
            mock_client.beta.files.upload.assert_called_once()

    @patch("html2md.upload.anthropic")
    @patch("html2md.upload.upload_file")
    def test_main_passes_client(self, mock_upload_file, mock_anthropic):
        """Test that main creates and passes a client to upload_file."""
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        # Mock argv
        argv = ["dummy.txt"]

        with patch("sys.stdout", new_callable=MagicMock):
            main(argv)

        mock_anthropic.Anthropic.assert_called_once()
        mock_upload_file.assert_called_once_with("dummy.txt", client=mock_client)
