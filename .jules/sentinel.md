
## 2024-05-18 - Hardcoded Bind to All Interfaces in Flask App
**Vulnerability:** The Flask application `app.py` was hardcoded to default to binding to all network interfaces (`0.0.0.0`), which could expose the development or production server to untrusted networks if deployed without proper network isolation.
**Learning:** Hardcoding `0.0.0.0` as the default host violates the principle of least privilege for network bindings. Applications should bind to `127.0.0.1` by default and require explicit configuration (e.g., via environment variables) to expose services externally. This was caught by Bandit static analysis.
**Prevention:** Default to `127.0.0.1` for local bindings. Use environment variables to allow operators to explicitly opt-in to binding to all interfaces when deploying in containers or behind reverse proxies. Ensure `bandit` or similar tools are run to detect `B104:hardcoded_bind_all_interfaces`.
