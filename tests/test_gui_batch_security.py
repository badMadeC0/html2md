"""Security regression tests for the PowerShell GUI batch mode."""

import shutil
import subprocess
from pathlib import Path

import pytest


def get_powershell_executable():
    """Return an available PowerShell executable, or None if unavailable."""
    for candidate in ("pwsh", "powershell"):
        executable = shutil.which(candidate)
        if executable is None:
            continue

        probe = subprocess.run(
            [
                executable,
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "$PSVersionTable.PSVersion.ToString()",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode == 0:
            return executable

    return None


PS_EXE = get_powershell_executable()


@pytest.mark.skipif(PS_EXE is None, reason="PowerShell not available on this system")
def test_batch_mode_rejects_unsupported_schemes(tmp_path):
    """Batch mode rejects non-HTTP(S) URLs before invoking the converter."""
    repo_script = Path(__file__).resolve().parents[1] / "gui-url-convert.ps1"
    script_path = tmp_path / "gui-url-convert.ps1"
    shutil.copyfile(repo_script, script_path)

    batch_file = tmp_path / "batch.txt"
    batch_file.write_text("file:///etc/passwd\nhttp://example.com\n", encoding="utf-8")

    cmd = [
        PS_EXE,
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(script_path),
        "-BatchFile",
        str(batch_file),
        "-BatchOutDir",
        str(tmp_path / "out"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    combined_output = result.stdout + result.stderr
    assert "Skipping invalid URL: file:///etc/passwd" in combined_output
    assert "Processing: http://example.com/" in result.stdout
