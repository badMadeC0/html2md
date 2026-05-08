"""Tests for html2md CLI exception-handling paths."""

import unittest
from unittest.mock import patch, MagicMock
import io
import requests  # type: ignore[import-untyped]
from html2md.cli import main


class TestCliExceptions(unittest.TestCase):
    """Unit tests for CLI network, file, and path-containment error handling."""

    def test_network_error(self):
        """Test that network errors are caught and printed."""
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

    def test_file_error(self):
        """Test that file I/O errors are caught and printed."""
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

    def test_outdir_containment_uses_path_aware_check(self):
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
                        # Verify a rejected output path is never opened for writing.
                        def fake_realpath(path):
                            if str(path).endswith(".md"):
                                return "/tmp/outside/a.md"
                            return "/tmp/out"

                        real_open = open
                        opened_output_paths = []

                        def tracking_open(path, *args, **kwargs):
                            if str(path) == "/tmp/out/a.md":
                                opened_output_paths.append(str(path))
                            return real_open(path, *args, **kwargs)

                        with patch("builtins.open", side_effect=tracking_open):
                            with patch("os.path.realpath", side_effect=fake_realpath):
                                main(
                                    [
                                        "--url",
                                        "http://example.com/a",
                                        "--outdir",
                                        "/tmp/out",
                                    ]
                                )

                            self.assertEqual([], opened_output_paths)

                        output = captured_stderr.getvalue()
                        self.assertIn("Output path escapes output directory", output)
