from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gui_launcher_uses_file_mode_for_paths() -> None:
    launcher = (ROOT / "run-gui.bat").read_text(encoding="utf-8")

    assert "-Command" not in launcher
    assert '-File "%SCRIPT_DIR%gui-url-convert.ps1"' in launcher
    assert "Set-Location -LiteralPath '%SCRIPT_DIR%'" not in launcher


def test_gui_script_single_url_mode_uses_env_vars_not_interpolation() -> None:
    """Single URL mode must not interpolate user-controlled values into -Command strings."""
    script = (ROOT / "gui-url-convert.ps1").read_text(encoding="utf-8")

    # The old unsafe single-URL sanitization patterns must be gone
    assert "$safeUrl = $url -replace" not in script
    assert "$safeVenvExe = $venvExe -replace" not in script
    assert "$safePyScript = $pyScript -replace" not in script

    # User-controlled paths must be passed via env vars, not interpolated
    assert 'HTML2MD_URL' in script
    assert 'HTML2MD_OUTDIR' in script

    # Env vars must be cleaned up after process launch
    assert '[Environment]::SetEnvironmentVariable("HTML2MD_URL",       $null, "Process")' in script
    assert '[Environment]::SetEnvironmentVariable("HTML2MD_OUTDIR",    $null, "Process")' in script
    assert '[Environment]::SetEnvironmentVariable("HTML2MD_EXE",       $null, "Process")' in script
    assert '[Environment]::SetEnvironmentVariable("HTML2MD_PY_SCRIPT", $null, "Process")' in script
