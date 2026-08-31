## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-08-31 - Added Security Headers to Flask Application
**Vulnerability:** The Flask application (`src/html2md/app.py`) was returning HTTP responses without baseline security headers, leaving clients exposed to potential MIME-sniffing and clickjacking attacks.
**Learning:** Even simple healthcheck or API endpoints should include baseline security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`) to ensure defense-in-depth and establish good security posture from the start.
**Prevention:** Implement an `@app.after_request` hook to enforce strict security headers globally across all routes.
