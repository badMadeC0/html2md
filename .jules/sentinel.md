## 2024-05-24 - Missing Security Headers in Flask App
**Vulnerability:** The Flask application (`src/html2md/app.py`) was serving API responses without common security headers (e.g., `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Content-Security-Policy`).
**Learning:** Default Flask apps do not automatically enforce these headers, requiring an `@app.after_request` handler.
**Prevention:** Always add a global response hook for security headers when bootstrapping new Flask or similar framework web applications to establish defense in depth against XSS, clickjacking, and MIME sniffing.

## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
