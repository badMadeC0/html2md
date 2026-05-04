## 2026-05-04 - Fix hardcoded bind all interfaces in app.py
**Vulnerability:** The Flask application in `app.py` was defaulting to binding on all interfaces (`0.0.0.0`), exposing it to potentially untrusted networks.
**Learning:** Hardcoded bind addresses mapping to all interfaces can inadvertently expose an application, leading to unauthorized access.
**Prevention:** Use `127.0.0.1` as the default bind address, and allow overriding via environment variables (e.g. `HOST`).
