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


def test_batch_mode_passes_delete_batch_file_switch() -> None:
    gui_script = (ROOT / "gui-url-convert.ps1").read_text(encoding="utf-8")

    # Batch mode must append -DeleteBatchFile so the subprocess cleans up
    # the GUI-created temp file.
    assert '$psi.Arguments += " -DeleteBatchFile"' in gui_script


def test_delete_batch_file_guarded_by_batch_file_param() -> None:
    gui_script = (ROOT / "gui-url-convert.ps1").read_text(encoding="utf-8")

    # The finally cleanup must check $BatchFile is non-empty before calling
    # Remove-Item, so passing -DeleteBatchFile with only -Url does not cause
    # a parameter-binding error.
    assert "$DeleteBatchFile -and $BatchFile" in gui_script
