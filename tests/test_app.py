import pytest

try:
    import flask  # noqa: F401
except ImportError:
    pytest.skip("flask is not installed", allow_module_level=True)

from html2md.app import get_host_port, DEFAULT_PORT


def test_get_host_port_invalid_port(capsys, monkeypatch):
    monkeypatch.setenv("PORT", "not-an-int")

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT

    captured = capsys.readouterr()
    assert "Warning: Invalid PORT environment variable value" in captured.out
    assert "'not-an-int'" in captured.out
