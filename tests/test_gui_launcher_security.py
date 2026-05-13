from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gui_launcher_uses_file_mode_for_paths() -> None:
    launcher = (ROOT / "run-gui.bat").read_text(encoding="utf-8")

    assert "-Command" not in launcher
    assert '-File "%SCRIPT_DIR%gui-url-convert.ps1"' in launcher
    assert "Set-Location -LiteralPath '%SCRIPT_DIR%'" not in launcher


def test_gui_script_avoids_command_relaunch() -> None:
    gui_script = (ROOT / "gui-url-convert.ps1").read_text(encoding="utf-8")

    # The script should not use -Command to relaunch itself or other processes for conversion.
    # We allow it in comments or help text, but not in the active code for launching.
    # Specifically, check the $psi.Arguments lines.
    active_arguments = [line for line in gui_script.splitlines() if "$psi.Arguments =" in line]
    for line in active_arguments:
        assert "-Command" not in line
        assert "-File" in line
