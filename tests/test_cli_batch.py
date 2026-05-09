"""Batch-mode tests for CLI URL processing."""

from unittest.mock import MagicMock, patch

from html2md.cli import main


def _mock_response(text="<h1>Hello</h1>"):
    response = MagicMock()
    response.text = text
    response.raise_for_status.return_value = None
    return response


def test_batch_fetch_uses_separate_session_per_url(tmp_path):
    """Each batch URL gets its own requests.Session instance."""
    batch_file = tmp_path / "urls.txt"
    batch_file.write_text(
        "http://example.com/one\nhttp://example.com/two\n", encoding="utf-8"
    )
    created_sessions = []

    def session_factory():
        session = MagicMock()
        session.get.return_value = _mock_response()
        created_sessions.append(session)
        return session

    with patch("requests.Session", side_effect=session_factory):
        with patch("markdownify.markdownify", return_value="# Hello"):
            assert main(["--batch", str(batch_file)]) == 0

    assert len(created_sessions) == 2
    assert created_sessions[0] is not created_sessions[1]
    for session in created_sessions:
        session.get.assert_called_once()
        session.close.assert_called_once()


def test_session_creation_failure_is_reported_without_masking(capsys):
    """Session creation failures should be reported without close() masking them."""
    with patch("requests.Session", side_effect=RuntimeError("session boom")):
        assert main(["--url", "http://example.com"]) == 0

    captured = capsys.readouterr()
    assert "Conversion failed: session boom" in captured.err
