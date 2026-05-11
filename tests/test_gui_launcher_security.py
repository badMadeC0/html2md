from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gui_launcher_uses_file_mode_for_paths() -> None:
    launcher = (ROOT / "run-gui.bat").read_text(encoding="utf-8")

    assert "-Command" not in launcher
    assert '-File "%SCRIPT_DIR%gui-url-convert.ps1"' in launcher
    assert "Set-Location -LiteralPath '%SCRIPT_DIR%'" not in launcher


def test_single_url_launch_uses_encoded_command() -> None:
    """Single-URL mode must use -EncodedCommand, not a nested -Command string.

    This guards against reintroduction of the raw nested -Command quoting issue
    where the native Windows command-line parser could strip or re-split quotes
    embedded in user-controlled paths/URLs.
    """
    script = (ROOT / "gui-url-convert.ps1").read_text(encoding="utf-8")

    # Locate the single-URL section so we only inspect that block.
    single_url_marker = "# --- SINGLE URL MODE ---"
    assert single_url_marker in script, "Single-URL mode marker not found in gui-url-convert.ps1"

    single_url_section = script[script.index(single_url_marker):]

    # The section must assign -EncodedCommand at least once.
    assert "-EncodedCommand" in single_url_section, (
        "Single-URL launch must use -EncodedCommand to avoid native quote-stripping"
    )

    # The section must NOT fall back to a raw nested -Command string.
    assert '"-NoExit -NoProfile -Command' not in single_url_section, (
        "Single-URL launch must not use a raw nested -Command string"
    )
    assert '"-NoExit -Command' not in single_url_section, (
        "Single-URL launch must not use a raw nested -Command string"
    )
