## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-05-08 - Flask Security Improvements
**Vulnerability:** The Flask application bound to `0.0.0.0` by default and lacked basic security headers.
**Learning:** Defaulting to `0.0.0.0` exposes the server to all network interfaces, which can be dangerous in some environments. Missing security headers leaves the app vulnerable to basic attacks like clickjacking and MIME-type sniffing.
**Prevention:** Always default network bindings to `127.0.0.1` unless explicitly configured otherwise via environment variables. Use `after_request` hooks to ensure security headers are consistently applied.
