## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Added Security Headers to Flask Application
**Vulnerability:** The Flask application in `src/html2md/app.py` returned HTTP responses without any security headers. This lack of defense-in-depth measures exposes the application to risks such as MIME-type sniffing (`X-Content-Type-Options`), clickjacking (`X-Frame-Options`), and cross-site scripting/data injection if browsers attempt to execute returned content.
**Learning:** Even simple API endpoints (like health checks) that return JSON must include baseline security headers to enforce secure browser behavior and prevent malicious framing or content sniffing.
**Prevention:** Always implement an `@app.after_request` hook (or use an extension like Flask-Talisman) to inject standard security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy: default-src 'none'`) into every response.
