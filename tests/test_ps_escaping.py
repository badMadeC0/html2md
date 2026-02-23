"""Verify PowerShell escaping logic."""
import pytest

def get_powershell_args(url, outdir):
    """Simulate PowerShell command construction logic to verify safety."""
    # Logic matches gui-url-convert.ps1
    safe_url = url.replace("'", "''")
    safe_outdir = outdir.replace("'", "''")
    return f"-NoExit -Command \"& '$venvExe' --url '{safe_url}' --outdir '{safe_outdir}' --all-formats\""

def test_ps_escaping_normal():
    """Test normal input escaping."""
    url = "http://example.com"
    outdir = r"C:\Downloads"
    args = get_powershell_args(url, outdir)
    # Expected output matching the escaping logic
    expected = '-NoExit -Command "& \'$venvExe\' --url \'http://example.com\' --outdir \'C:\\Downloads\' --all-formats"'
    assert args == expected

def test_ps_escaping_malicious_url():
    """Test malicious URL escaping preventing command injection."""
    url = "http://example.com'; Start-Process calc; '"
    outdir = r"C:\Downloads"

    args = get_powershell_args(url, outdir)

    # Expected: http://example.com''; Start-Process calc; '''
    expected = '-NoExit -Command "& \'$venvExe\' --url \'http://example.com\'\'; Start-Process calc; \'\'\' --outdir \'C:\\Downloads\' --all-formats"'
    assert args == expected

def test_ps_escaping_malicious_outdir():
    """Test malicious output directory escaping."""
    url = "http://example.com"
    outdir = r"C:\Downloads'; Remove-Item -Recurse *; '"

    args = get_powershell_args(url, outdir)

    expected = '-NoExit -Command "& \'$venvExe\' --url \'http://example.com\' --outdir \'C:\\Downloads\'\'; Remove-Item -Recurse *; \'\'\' --all-formats"'
    assert args == expected
