from __future__ import annotations

import sys
import types


def _ensure_flask_stub() -> None:
    """Inject a minimal Flask stub so html2md.app can be imported without Flask."""
    if "flask" in sys.modules:
        return

    flask_stub = types.ModuleType("flask")

    class _FakeFlask:
        def __init__(self, *args, **kwargs):
            pass

        def route(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator

    flask_stub.Flask = _FakeFlask
    flask_stub.jsonify = lambda *args, **kwargs: {}
    sys.modules["flask"] = flask_stub


_ensure_flask_stub()

# html2md.app may have been cached before our stub was in place; evict it.
sys.modules.pop("html2md.app", None)

from html2md.app import DEFAULT_PORT, get_host_port  # noqa: E402


def test_get_host_port_invalid_port(capsys, monkeypatch):
    monkeypatch.setenv("PORT", "not-an-int")
    monkeypatch.delenv("HOST", raising=False)

    host, port = get_host_port()

    assert host == "0.0.0.0"
    assert port == DEFAULT_PORT

    captured = capsys.readouterr()
    assert "Warning: Invalid PORT environment variable value" in captured.out
    assert "'not-an-int'" in captured.out
