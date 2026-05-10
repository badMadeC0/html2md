"""Tests for CLI batch URL processing."""

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

from html2md import cli


class _ImmediateFuture:
    def __init__(self, executor, value):
        self.executor = executor
        self.value = value

    def result(self):
        self.executor.in_flight -= 1
        return self.value


class _RecordingExecutor:
    def __init__(self):
        self.submitted = []
        self.in_flight = 0
        self.max_in_flight = 0

    def submit(self, func, item):
        self.submitted.append(item)
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        return _ImmediateFuture(self, func(item))


def test_ordered_bounded_map_caps_submitted_futures_before_first_result():
    """The ordered mapper does not eagerly submit the whole input iterable."""
    executor = _RecordingExecutor()
    results = cli._ordered_bounded_map(executor, lambda item: item * 2, range(10), 3)

    assert next(results) == 0
    assert executor.submitted == [0, 1, 2]
    assert executor.max_in_flight == 3

    assert list(results) == [2, 4, 6, 8, 10, 12, 14, 16, 18]
    assert executor.submitted == list(range(10))
    assert executor.max_in_flight == 3


def test_batch_outputs_results_in_input_order(monkeypatch, capsys, tmp_path):
    """Batch mode keeps deterministic output ordering across multiple URLs."""
    batch_file = tmp_path / "urls.txt"
    batch_file.write_text(
        "http://example.com/first\n\nhttp://example.com/second\n",
        encoding="utf-8",
    )

    session = MagicMock()

    def fake_get(url, timeout):
        response = MagicMock()
        response.text = f"<h1>{url.rsplit('/', 1)[-1]}</h1>"
        response.raise_for_status.return_value = None
        return response

    session.get.side_effect = fake_get
    monkeypatch.setitem(
        sys.modules,
        "requests",
        SimpleNamespace(Session=lambda: session, RequestException=Exception),
    )
    monkeypatch.setitem(
        sys.modules,
        "markdownify",
        SimpleNamespace(markdownify=lambda html, heading_style: html),
    )

    assert cli.main(["--batch", str(batch_file)]) == 0

    captured = capsys.readouterr()
    first_idx = captured.out.index("Processing URL: http://example.com/first")
    second_idx = captured.out.index("Processing URL: http://example.com/second")
    assert first_idx < second_idx
    assert "<h1>first</h1>" in captured.out
    assert "<h1>second</h1>" in captured.out
