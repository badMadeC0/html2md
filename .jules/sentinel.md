## 2024-05-15 - [Secure Default Host Binding]
**Vulnerability:** The Flask application in `app.py` was defaulting to binding on `0.0.0.0` (all interfaces) if the `HOST` environment variable was not set.
**Learning:** Defaulting to `0.0.0.0` can unintentionally expose local development servers or internal services to the network, increasing the attack surface.
**Prevention:** Always default network services to bind to `127.0.0.1` (localhost) unless explicitly configured otherwise via environment variables or configuration files. This enforces a secure-by-default posture.