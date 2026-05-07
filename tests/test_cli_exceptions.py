"""Tests for html2md CLI exception-handling paths."""

import socket
import unittest
from unittest.mock import patch, MagicMock
import io
import requests  # type: ignore[import-untyped]
from html2md.cli import main


class TestCliExceptions(unittest.TestCase):
    """Unit tests for CLI network, file, and path-containment error handling."""

    @patch("html2md.cli.socket.getaddrinfo")
    def test_network_error(self, mock_getaddrinfo):
        """Test that network errors are caught and printed."""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))
        ]
        captured_stderr = io.StringIO()
        with patch("sys.stderr", captured_stderr):
            with patch("requests.Session.get") as mock_get:
                mock_get.side_effect = requests.RequestException("Network unreachable")

                try:
                    main(["--url", "http://example.com"])
                except (SystemExit, RuntimeError, ValueError) as e:
                    self.fail(f"main raised exception {e}")

                output = captured_stderr.getvalue()
                self.assertIn("Network error", output)
                self.assertIn("Network unreachable", output)

    @patch("html2md.cli.socket.getaddrinfo")
    def test_file_error(self, mock_getaddrinfo):
        """Test that file I/O errors are caught and printed."""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))
        ]
        captured_stderr = io.StringIO()
        with patch("sys.stderr", captured_stderr):
            with patch("requests.Session.get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.text = "<h1>Hello</h1>"
                mock_resp.status_code = 200
                mock_get.return_value = mock_resp

                with patch("markdownify.markdownify", return_value="# Hello"):
                    with patch("os.makedirs"), patch(
                        "os.path.exists", return_value=False
                    ):
                        with patch(
                            "builtins.open", side_effect=OSError("Permission denied")
                        ):
                            try:
                                main(
                                    ["--url", "http://example.com", "--outdir", "dummy"]
                                )
                            except (SystemExit, RuntimeError, ValueError) as e:
                                self.fail(f"main raised exception {e}")

                            output = captured_stderr.getvalue()
                            self.assertIn("File error", output)
                            self.assertIn("Permission denied", output)

    @patch("html2md.cli.is_safe_url", return_value=True)
    def test_outdir_containment_uses_path_aware_check(self, mock_is_safe_url):
        """Test that output containment check rejects prefix-matching escapes."""
        captured_stderr = io.StringIO()
        with patch("sys.stderr", captured_stderr):
            with patch("requests.Session.get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.text = "<h1>Hello</h1>"
                mock_resp.status_code = 200
                mock_get.return_value = mock_resp

                with patch("markdownify.markdownify", return_value="# Hello"):
                    with patch("os.path.exists", return_value=True):
                        # Mock the open used in cli.py instead of builtins.open to avoid breaking argparse locale loading
                        with patch("html2md.cli.open") as mock_open:

                            def fake_realpath(path):
                                if str(path).endswith(".md"):
                                    return "/tmp/outside/a.md"
                                return "/tmp/out"

                            with patch("os.path.realpath", side_effect=fake_realpath):
                                main(
                                    [
                                        "--url",
                                        "http://example.com/a",
                                        "--outdir",
                                        "/tmp/out",
                                    ]
                                )

                            output = captured_stderr.getvalue()
                            self.assertIn(
                                "Output path escapes output directory", output
                            )
                            mock_open.assert_not_called()
