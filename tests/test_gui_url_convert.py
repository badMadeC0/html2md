"""Regression tests for the PowerShell GUI launch arguments."""

from pathlib import Path


GUI_SCRIPT = Path(__file__).resolve().parents[1] / "gui-url-convert.ps1"


def test_gui_does_not_pass_unsupported_cli_flags():
    """The GUI should only pass options registered by src/html2md/cli.py."""
    script = GUI_SCRIPT.read_text(encoding="utf-8")

    assert "--all-formats" not in script
    assert "--main-content" not in script


def test_gui_labels_match_supported_markdown_conversion():
    """The visible controls should not advertise unsupported all-format output."""
    script = GUI_SCRIPT.read_text(encoding="utf-8")

    assert 'Content="_Convert (Markdown)"' in script
    assert 'Content="Convert _Whole Page (CLI default)"' in script
    assert 'IsEnabled="False"' in script
