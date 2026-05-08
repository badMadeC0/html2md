"""Tests for batch URL processing."""

import time
from unittest.mock import MagicMock, patch

from html2md import cli

MOCK_SLOW_URL_DELAY = 0.05


def test_batch_stdout_is_emitted_in_input_order(capsys, tmp_path):
    """Concurrent batch conversion without --outdir prints in batch-file order."""
    batch_file = tmp_path / "urls.txt"
    batch_file.write_text(
        "http://example.com/slow\nhttp://example.com/fast\n",
        encoding="utf-8",
    )

    def get_response(url, **_kwargs):
        if url.endswith("/slow"):
            time.sleep(MOCK_SLOW_URL_DELAY)
        response = MagicMock()
        response.text = f"<h1>{url.rsplit('/', 1)[-1]}</h1>"
        response.raise_for_status.return_value = None
        return response

    with patch("requests.Session.get", side_effect=get_response):
        cli.main(["--batch", str(batch_file)])

    output = capsys.readouterr().out
    slow_heading = output.index("# slow")
    fast_heading = output.index("# fast")
    assert slow_heading < fast_heading
