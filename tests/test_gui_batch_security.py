"""Test batch mode URL scheme validation in the GUI wrapper."""

import shutil
import subprocess

import pytest


def get_powershell_command():
    """Find an available PowerShell executable with hermetic invocation flags."""
    for exe in ["pwsh", "powershell"]:
        cmd = [exe, "-NoProfile", "-NonInteractive", "-Command", "'1'"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            if result.returncode == 0:
                return [exe, "-NoProfile", "-NonInteractive"]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


PS_CMD = get_powershell_command()


@pytest.mark.skipif(PS_CMD is None, reason="PowerShell not available on this system")
def test_batch_mode_rejects_unsupported_schemes(tmp_path):
    """Batch mode rejects unsupported URL schemes before conversion."""
    repo_script = "gui-url-convert.ps1"
    isolated_script = tmp_path / repo_script
    shutil.copyfile(repo_script, isolated_script)

    batch_file = tmp_path / "batch.txt"
    batch_file.write_text("file:///etc/passwd\nhttp://example.com\n", encoding="utf-8")

    cmd = [
        *PS_CMD,
        "-File",
        str(isolated_script),
        "-BatchFile",
        str(batch_file),
        "-BatchOutDir",
        str(tmp_path / "out"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Skipping invalid URL: file:///etc/passwd" in combined_output
    assert "Processing: http://example.com/" in result.stdout
