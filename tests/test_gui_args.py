"""Tests for GUI command-line arguments."""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GUI_SCRIPT = REPO_ROOT / "gui-url-convert.ps1"


def test_gui_passes_only_supported_converter_flags():
    """The GUI should not pass converter flags that the bundled CLI cannot parse."""
    script = GUI_SCRIPT.read_text(encoding="utf-8")

    assert "--url" in script
    assert "--outdir" in script
    assert "--all-formats" not in script
    assert "--main-content" not in script
