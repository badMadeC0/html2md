import os
import shutil
import subprocess

import pytest


def get_powershell_executable():
    """Return a usable PowerShell executable, or None when unavailable."""
    for exe in ("pwsh", "powershell"):
        path = shutil.which(exe)
        if not path:
            continue
        result = subprocess.run(
            [path, "-NoProfile", "-NonInteractive", "-Command", "$PSVersionTable.PSVersion"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return path
    return None


PS_EXE = get_powershell_executable()


@pytest.mark.skipif(PS_EXE is None, reason="PowerShell not available on this system")
def test_batch_mode_rejects_unsupported_schemes(tmp_path):
    """Batch mode should reject unsupported schemes before conversion runs."""
    source_script = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../gui-url-convert.ps1")
    )
    script_path = tmp_path / "gui-url-convert.ps1"
    shutil.copyfile(source_script, script_path)

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
        str(tmp_path / "dummy_out"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    invalid_message = "Skipping invalid URL: file:///etc/passwd"
    assert invalid_message in result.stderr or invalid_message in result.stdout
    assert "Processing: http://example.com/" in result.stdout
