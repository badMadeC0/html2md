from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gui_launcher_uses_file_mode_for_paths() -> None:
    launcher = (ROOT / "run-gui.bat").read_text(encoding="utf-8")

    assert "-Command" not in launcher
    assert '-File "%SCRIPT_DIR%gui-url-convert.ps1"' in launcher
    assert "Set-Location -LiteralPath '%SCRIPT_DIR%'" not in launcher


def test_gui_outdir_dangerous_character_regex_is_closed() -> None:
    script = (ROOT / "gui-url-convert.ps1").read_text(encoding="utf-8")

    assert EXPECTED_OUTDIR_REGEX in script
    assert '$outdir -match \'[&|;<>^"%\\]\'' not in script
