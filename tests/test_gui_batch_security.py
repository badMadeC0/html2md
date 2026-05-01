"""Test batch mode URL scheme validation in the GUI wrapper."""

import os
import subprocess
import tempfile
import pytest

def get_powershell_executable():
    """Find available PowerShell executable."""
    for exe in ["pwsh", "powershell"]:
        try:
            r = subprocess.run([exe, "-Command", "echo 1"], capture_output=True, text=True, check=False)
            if r.returncode == 0:
                return exe
        except FileNotFoundError:
            continue
    return None

PS_EXE = get_powershell_executable()

@pytest.mark.skipif(PS_EXE is None, reason="PowerShell not available on this system")
def test_batch_mode_rejects_unsupported_schemes():
    """Test that the batch mode loop in gui-url-convert.ps1 rejects file:// schemes."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gui-url-convert.ps1"))

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as tf:
        tf.write("file:///etc/passwd\nhttp://example.com\n")
        batch_file = tf.name

    try:
        cmd = [PS_EXE, "-File", script_path, "-BatchFile", batch_file, "-BatchOutDir", "dummy_out"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Verify that file:// was rejected
        assert "Skipping invalid URL: file:///etc/passwd" in result.stderr or "Skipping invalid URL: file:///etc/passwd" in result.stdout

        # Verify that http:// was processed
        assert "Processing: http://example.com/" in result.stdout

    finally:
        os.remove(batch_file)
