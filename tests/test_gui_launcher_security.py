from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gui_launcher_uses_file_mode_for_paths() -> None:
    launcher = (ROOT / "run-gui.bat").read_text()

    assert "-Command" not in launcher
    assert '-File "%SCRIPT_DIR%gui-url-convert.ps1"' in launcher
    assert "Set-Location -LiteralPath '%SCRIPT_DIR%'" not in launcher
