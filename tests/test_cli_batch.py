"""Tests for CLI batch processing behavior."""

import os
from unittest.mock import MagicMock, patch

from html2md import cli


@patch("requests.Session.get")
def test_batch_creates_missing_outdir_idempotently(mock_get, monkeypatch, tmp_path):
    """Parallel batch writes create the output directory without racing."""
    batch_file = tmp_path / "urls.txt"
    batch_file.write_text(
        "http://example.com/posts/first\nhttp://example.com/posts/second\n",
        encoding="utf-8",
    )
    outdir = tmp_path / "output"

    response = MagicMock()
    response.text = "<h1>Hello</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    real_exists = os.path.exists
    real_makedirs = os.makedirs

    def stale_outdir_exists(path):
        if path == str(outdir):
            return False
        return real_exists(path)

    def racey_makedirs(path, *args, **kwargs):
        if (
            path == str(outdir)
            and outdir.exists()
            and not kwargs.get("exist_ok", False)
        ):
            raise FileExistsError(path)
        return real_makedirs(path, *args, **kwargs)

    monkeypatch.setattr(os.path, "exists", stale_outdir_exists)
    monkeypatch.setattr(os, "makedirs", racey_makedirs)

    cli.main(["--batch", str(batch_file), "--outdir", str(outdir)])

    assert (outdir / "first.md").read_text(encoding="utf-8").strip() == "# Hello"
    assert (outdir / "second.md").read_text(encoding="utf-8").strip() == "# Hello"


def test_batch_consumes_executor_results(monkeypatch, tmp_path):
    """Batch processing consumes executor results so worker exceptions surface."""
    batch_file = tmp_path / "urls.txt"
    batch_file.write_text("http://example.com/posts/first\n", encoding="utf-8")

    class RaisingExecutor:
        def __init__(self, max_workers):
            self.max_workers = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def map(self, func, iterable):
            def results():
                raise RuntimeError("worker failed")
                yield  # pragma: no cover

            return results()

    monkeypatch.setattr("concurrent.futures.ThreadPoolExecutor", RaisingExecutor)

    try:
        cli.main(["--batch", str(batch_file)])
    except RuntimeError as exc:
        assert str(exc) == "worker failed"
    else:
        raise AssertionError("worker exception was not surfaced")
