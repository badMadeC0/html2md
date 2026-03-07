"""Security tests for CLI."""

from html2md.cli import main

def test_cli_ssrf_protection_file_scheme(capsys):
    """Test that file:// scheme is rejected by the CLI."""
    argv = ['--url', 'file:///etc/passwd']
    ret = main(argv)

    assert ret == 0  # main returns 0 even on individual url failure as per original logic
    captured = capsys.readouterr()
    assert "Security Error: Invalid URL scheme for 'file:///etc/passwd'" in captured.out

def test_cli_ssrf_protection_ftp_scheme(capsys):
    """Test that ftp:// scheme is rejected by the CLI."""
    argv = ['--url', 'ftp://example.com/file.txt']
    ret = main(argv)

    assert ret == 0
    captured = capsys.readouterr()
    assert "Security Error: Invalid URL scheme for 'ftp://example.com/file.txt'" in captured.out

def test_cli_ssrf_protection_no_scheme(capsys):
    """Test that missing scheme is rejected by the CLI."""
    argv = ['--url', 'www.example.com']
    ret = main(argv)

    assert ret == 0
    captured = capsys.readouterr()
    assert "Security Error: Invalid URL scheme for 'www.example.com'" in captured.out
