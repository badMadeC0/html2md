"""Tests for CLI --batch mode."""

from __future__ import annotations

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest


@contextmanager
def html_server(responses: dict[str, str]):
    """Serve fixed HTML responses from localhost for CLI subprocess tests."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - stdlib callback name
            if self.path not in responses:
                self.send_error(404)
                return

            body = responses[self.path].encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):  # noqa: A002 - stdlib callback name
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


class TestCliBatch(unittest.TestCase):
    """CLI subprocess tests for --batch mode."""

    def run_html2md(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run the installed html2md console script with the given arguments."""
        html2md = shutil.which("html2md")
        if html2md is None:
            self.skipTest("html2md console script is not installed")

        return subprocess.run(
            [html2md, *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_batch_mode_success(self):
        """Batch mode processes non-empty URLs from a file through the CLI."""
        with tempfile.TemporaryDirectory() as tmp_dir, html_server(
            {
                "/1": "<h1>First</h1>",
                "/2": "<h1>Second</h1>",
            }
        ) as base_url:
            batch_file = Path(tmp_dir) / "urls.txt"
            batch_file.write_text(
                f"{base_url}/1\n  \n{base_url}/2 \n\n", encoding="utf-8"
            )

            result = self.run_html2md("--batch", str(batch_file))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertIn(f"Processing URL: {base_url}/1", result.stdout)
            self.assertIn(f"Processing URL: {base_url}/2", result.stdout)
            self.assertIn("# First", result.stdout)
            self.assertIn("# Second", result.stdout)

    def test_batch_mode_file_not_found(self):
        """Batch mode reports an error for a missing URL file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing_file = Path(tmp_dir) / "missing-urls.txt"

            result = self.run_html2md("--batch", str(missing_file))

            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn(
                f"Error: Batch file not found: {missing_file}",
                result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
