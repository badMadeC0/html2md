from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_GUI = REPO_ROOT / "run-gui.bat"


def test_run_gui_passes_batch_file_argument_without_powershell_command_interpolation():
    contents = RUN_GUI.read_text(encoding="utf-8")

    assert "-File \"%SCRIPT_DIR%gui-url-convert.ps1\" -BatchFile \"%~1\"" in contents
    assert "-Command" not in contents
    assert "-BatchFile '%~1'" not in contents
