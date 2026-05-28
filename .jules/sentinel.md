## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-05-28 - Bound Flask app to localhost by default
**Vulnerability:** The Flask application in `app.py` previously bound to `0.0.0.0` by default when no `HOST` environment variable was provided, potentially exposing the application across all network interfaces instead of restricting it to local loopback.
**Learning:** Default configurations should always favor local containment and explicit override patterns for public interfaces to prevent unintended external exposure.
**Prevention:** Hardcode default network bindings to `127.0.0.1` and rely on environment variable configuration for broader exposure when strictly required in deployed environments.
