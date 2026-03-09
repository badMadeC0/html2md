import os
import sys
import subprocess
import pytest
from pathlib import Path

# Identify if we're on Windows
IS_WINDOWS = sys.platform == "win32"

def test_temp_venv_wrapper_html2md():
    """
    Test that the run-html2md wrapper script works and successfully runs html2md --help.
    This also implicitly tests the temp-venv creation and caching logic inside the wrapper.
    """
    # Calculate path to wrapper based on OS
    repo_root = Path(__file__).resolve().parent.parent

    if IS_WINDOWS:
        script_path = repo_root / "run-html2md.bat"
        # On Windows, run the batch script through cmd
        cmd = ["cmd.exe", "/c", str(script_path), "--help"]
    else:
        script_path = repo_root / "run-html2md.sh"
        if not script_path.exists():
            pytest.skip(f"Wrapper script {script_path} not found")

        # Ensure it's executable
        os.chmod(script_path, 0o755)
        # On Mac/Linux, run the shell script
        cmd = [str(script_path), "--help"]

    # Run the subprocess
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # Give it time to build wheels on first run
        )
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Wrapper script failed with return code {e.returncode}.\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
    except subprocess.TimeoutExpired:
        pytest.fail("Wrapper script timed out.")

    # Verify standard wrapper output (logging prefixes) and html2md output
    assert "[INFO]" in result.stdout
    assert "Using cache directory:" in result.stdout
    assert "Creating temporary virtual environment:" in result.stdout

    # Check that html2md actually ran inside the wrapper
    assert "usage:" in result.stdout.lower() or "options:" in result.stdout.lower()

    # We can also verify that the temp venv is cleaned up. However, since the script runs
    # in its own context and we don't necessarily know the exact random dirname from here without
    # parsing, we trust the script's internal cleanup mechanism. The fact that it exits 0 means
    # the cleanup trap/logic executed successfully.

@pytest.mark.skipif(not IS_WINDOWS, reason="GUI wrapper natively requires Windows/PowerShell.")
def test_temp_venv_wrapper_gui():
    """
    Smoke test the GUI wrapper on Windows. We won't actually launch the GUI
    to avoid blocking the test runner, but we can verify the script exists
    and is formatted correctly, or run a harmless help command if it supports one.
    For now, just verify the batch file exists since running a GUI in CI is problematic.
    """
    repo_root = Path(__file__).resolve().parent.parent
    script_path = repo_root / "run-gui.bat"

    assert script_path.exists()
    content = script_path.read_text(encoding='utf-8')

    assert "html2md-venv-" in content
    assert "html2md-cache" in content
    assert "pip install" in content
    assert "rmdir /s /q" in content  # Cleanup logic exists

@pytest.mark.skipif(IS_WINDOWS, reason="Unix specific wrapper check")
def test_temp_venv_wrapper_gui_unix():
    """
    Verify the Unix GUI wrapper exists and contains the correct fallback warning logic.
    """
    repo_root = Path(__file__).resolve().parent.parent
    script_path = repo_root / "run-gui.sh"

    assert script_path.exists()
    content = script_path.read_text(encoding='utf-8')

    assert "mktemp" in content
    assert "html2md-venv-" in content
    assert "html2md-cache" in content
    assert "gui-url-convert.ps1 is a Windows Presentation Foundation" in content
