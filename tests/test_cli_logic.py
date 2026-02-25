import sys
import os
import unittest
import builtins
import logging
from unittest.mock import patch, MagicMock, mock_open

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli


class TestGetUniqueFilepath(unittest.TestCase):
    """Tests for get_unique_filepath helper function."""

    def test_file_does_not_exist(self):
        """Test when file does not exist, it returns the original path."""
        with patch("os.path.exists", return_value=False):
            result = html2md.cli.get_unique_filepath("test.md")
            self.assertEqual(result, "test.md")

    def test_file_exists_once(self):
        """Test when file exists, it appends (1)."""
        # side_effect: first call (original) returns True, second (with 1) returns False
        with patch("os.path.exists", side_effect=[True, False]):
            result = html2md.cli.get_unique_filepath("test.md")
            self.assertEqual(result, "test (1).md")

    def test_file_exists_multiple(self):
        """Test when file exists multiple times, it increments the counter."""
        # side_effect: original -> True, (1) -> True, (2) -> False
        with patch("os.path.exists", side_effect=[True, True, False]):
            result = html2md.cli.get_unique_filepath("test.md")
            self.assertEqual(result, "test (2).md")


class TestMain(unittest.TestCase):
    """Tests for main CLI function."""

    def setUp(self):
        # Mocks for dependencies that are imported inside main
        self.mock_requests = MagicMock()
        self.mock_markdownify = MagicMock()
        self.mock_bs4 = MagicMock()
        self.mock_reportlab_platypus = MagicMock()
        self.mock_reportlab_styles = MagicMock()

        self.modules_patch = patch.dict(
            sys.modules,
            {
                "requests": self.mock_requests,
                "markdownify": self.mock_markdownify,
                "bs4": self.mock_bs4,
                "reportlab.platypus": self.mock_reportlab_platypus,
                "reportlab.lib.styles": self.mock_reportlab_styles,
            },
        )
        self.modules_patch.start()

    def tearDown(self):
        self.modules_patch.stop()

    def test_help_only(self):
        """Test --help-only argument."""
        with patch("argparse.ArgumentParser.print_help") as mock_print_help:
            ret = html2md.cli.main(["--help-only"])
            self.assertEqual(ret, 0)
            mock_print_help.assert_called_once()

    def test_no_args(self):
        """Test running with no arguments."""
        with patch("argparse.ArgumentParser.print_help") as mock_print_help:
            ret = html2md.cli.main([])
            self.assertEqual(ret, 0)
            mock_print_help.assert_called_once()

    def test_missing_dependencies(self):
        """Test behavior when dependencies are missing."""
        # Stop the setUp patch so we can apply a failing one
        self.modules_patch.stop()

        original_import = builtins.__import__

        def side_effect(name, *args, **kwargs):
            if name == "requests":
                raise ImportError("No module named 'requests'", name="requests")
            return original_import(name, *args, **kwargs)

        # We need to ensure 'requests' is not in sys.modules so the import is triggered
        with patch.dict(sys.modules):
            if "requests" in sys.modules:
                del sys.modules["requests"]

            with patch("builtins.__import__", side_effect=side_effect):
                # Capture logging
                with self.assertLogs(level="ERROR") as log:
                    ret = html2md.cli.main(["--url", "http://example.com"])
                    self.assertEqual(ret, 1)
                    # Check if expected error message is in logs
                    self.assertTrue(
                        any("Missing dependency requests" in m for m in log.output)
                    )

        # Restart patch for tearDown
        self.modules_patch.start()

    def test_simple_conversion_stdout(self):
        """Test simple URL conversion printing to stdout."""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.text = "<html><body><h1>Hello</h1></body></html>"
        self.mock_requests.Session.return_value.get.return_value = mock_response
        self.mock_markdownify.markdownify.return_value = "# Hello"

        with patch("builtins.print") as mock_print:
            ret = html2md.cli.main(["--url", "http://example.com"])

            self.assertEqual(ret, 0)
            self.mock_requests.Session.return_value.get.assert_called_with(
                "http://example.com", timeout=30
            )
            self.mock_markdownify.markdownify.assert_called()
            mock_print.assert_called_with("# Hello")

    def test_file_output(self):
        """Test conversion saving to file."""
        mock_response = MagicMock()
        mock_response.text = "<html>Content</html>"
        self.mock_requests.Session.return_value.get.return_value = mock_response
        self.mock_markdownify.markdownify.return_value = "Content"

        mock_file = mock_open()
        original_open = builtins.open

        def side_effect(file, *args, **kwargs):
            if isinstance(file, str) and "output" in file:
                return mock_file(file, *args, **kwargs)
            return original_open(file, *args, **kwargs)

        # Mock os.makedirs and open
        with patch("os.makedirs") as mock_makedirs, patch(
            "builtins.open", side_effect=side_effect
        ), patch(
            "os.path.exists", return_value=False
        ):  # Directory and file don't exist

            ret = html2md.cli.main(
                ["--url", "http://example.com/foo", "--outdir", "output"]
            )

            self.assertEqual(ret, 0)
            mock_makedirs.assert_called_with("output")

            # Check if file was opened for writing
            # Since we used side_effect, we can check mock_file calls
            args, _ = mock_file.call_args
            self.assertTrue(args[0].endswith(".md"))
            self.assertEqual(args[1], "w")
            mock_file().write.assert_called_with("Content")

    def test_all_formats(self):
        """Test --all-formats option."""
        mock_response = MagicMock()
        mock_response.text = "<html>Content</html>"
        self.mock_requests.Session.return_value.get.return_value = mock_response
        self.mock_markdownify.markdownify.return_value = "Content"

        # Mock BeautifulSoup for TXT extraction
        mock_soup = MagicMock()
        mock_soup.get_text.return_value = "Content Text"
        self.mock_bs4.BeautifulSoup.return_value = mock_soup

        mock_file = mock_open()
        original_open = builtins.open

        def side_effect(file, *args, **kwargs):
            if isinstance(file, str) and "out" in file:
                return mock_file(file, *args, **kwargs)
            return original_open(file, *args, **kwargs)

        with patch("os.makedirs"), patch(
            "builtins.open", side_effect=side_effect
        ), patch("os.path.exists", return_value=False):

            ret = html2md.cli.main(
                ["--url", "http://example.com", "--outdir", "out", "--all-formats"]
            )

            self.assertEqual(ret, 0)

            # Check for TXT write
            mock_file().write.assert_any_call("Content Text")

            # Check PDF generation
            self.mock_reportlab_platypus.SimpleDocTemplate.assert_called()
            self.mock_reportlab_platypus.SimpleDocTemplate.return_value.build.assert_called()

    def test_main_content_extraction(self):
        """Test --main-content option."""
        mock_response = MagicMock()
        mock_response.text = (
            "<html><body><nav>Menu</nav><main>Main Content</main></body></html>"
        )
        self.mock_requests.Session.return_value.get.return_value = mock_response

        mock_soup = MagicMock()
        mock_main_tag = MagicMock()
        mock_main_tag.__str__.return_value = "<main>Main Content</main>"
        mock_soup.find.return_value = mock_main_tag
        self.mock_bs4.BeautifulSoup.return_value = mock_soup

        with patch("builtins.print"):
            html2md.cli.main(["--url", "http://example.com", "--main-content"])

            self.mock_bs4.BeautifulSoup.assert_called()
            mock_soup.find.assert_called_with("main")
            # The markdownify call should receive the main tag string
            self.mock_markdownify.markdownify.assert_called_with(
                "<main>Main Content</main>", heading_style="ATX"
            )

    def test_batch_processing(self):
        """Test --batch processing."""
        # Mock file content
        batch_content = "http://a.com\nhttp://b.com"

        # Setup conversion mocks
        mock_response = MagicMock()
        mock_response.text = "html"
        self.mock_requests.Session.return_value.get.return_value = mock_response

        original_open = builtins.open

        def side_effect(file, *args, **kwargs):
            if file == "urls.txt":
                return mock_open(read_data=batch_content)(file, *args, **kwargs)
            return original_open(file, *args, **kwargs)

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=side_effect
        ), patch("builtins.print"):

            ret = html2md.cli.main(["--batch", "urls.txt"])

            self.assertEqual(ret, 0)
            # Should have called get twice
            self.assertEqual(self.mock_requests.Session.return_value.get.call_count, 2)
            self.mock_requests.Session.return_value.get.assert_any_call(
                "http://a.com", timeout=30
            )
            self.mock_requests.Session.return_value.get.assert_any_call(
                "http://b.com", timeout=30
            )

    def test_url_correction(self):
        """Test that URLs with /? are corrected."""
        mock_response = MagicMock()
        mock_response.text = "html"
        self.mock_requests.Session.return_value.get.return_value = mock_response

        with patch("builtins.print"):
            html2md.cli.main(["--url", "http://example.com/?q=1"])

            # The actual call should be with ? instead of /?
            self.mock_requests.Session.return_value.get.assert_called_with(
                "http://example.com?q=1", timeout=30
            )


if __name__ == "__main__":
    unittest.main()
