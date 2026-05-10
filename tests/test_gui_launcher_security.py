from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gui_launcher_uses_file_mode_for_paths() -> None:
    launcher = (ROOT / "run-gui.bat").read_text(encoding="utf-8")

    assert "-Command" not in launcher
    assert '-File "%SCRIPT_DIR%gui-url-convert.ps1"' in launcher
    assert "Set-Location -LiteralPath '%SCRIPT_DIR%'" not in launcher


def test_gui_single_url_mode_avoids_command_reparsing() -> None:
    script = (ROOT / "gui-url-convert.ps1").read_text(encoding="utf-8")

    assert "[string]$SingleUrl" in script
    assert "-SingleUrl $safeUrl" in script
    assert '$psi.Arguments = "-NoExit -Command' not in script
    assert "prevents subexpressions such as $() in a URL from executing" in script


def test_gui_conversion_uses_argument_arrays_for_urls() -> None:
    script = (ROOT / "gui-url-convert.ps1").read_text(encoding="utf-8")

    assert '$argsList = @("--url", $Url, "--outdir", $OutDir, "--all-formats")' in script
    assert "& $venvExe @argsList" in script
    assert "& $pyCmd @pythonArgs" in script
