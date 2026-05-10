from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gui_launcher_uses_file_mode_for_paths() -> None:
    launcher = (ROOT / "run-gui.bat").read_text(encoding="utf-8")

    assert "-Command" not in launcher
    assert '-File "%SCRIPT_DIR%gui-url-convert.ps1"' in launcher
    assert "Set-Location -LiteralPath '%SCRIPT_DIR%'" not in launcher


def test_gui_single_url_launch_avoids_command_mode() -> None:
    launcher = (ROOT / "gui-url-convert.ps1").read_text(encoding="utf-8")

    assert "-NoExit -Command" not in launcher
    assert "-SingleUrl $safeUrl -SingleOutDir $safeOutDir" in launcher
    assert "ConvertTo-NativeCommandLineArgument $url" in launcher


def test_gui_single_url_handler_invokes_backend_with_argument_array() -> None:
    launcher = (ROOT / "gui-url-convert.ps1").read_text(encoding="utf-8")

    assert "[string]$SingleUrl" in launcher
    assert "& $venvExe @argsList" in launcher
    assert "& $pyCmd @argsList" in launcher
