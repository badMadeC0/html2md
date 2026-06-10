## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2025-03-12 - Missing Security Headers in Flask App
**Vulnerability:** The Flask application `src/html2md/app.py` was serving responses without essential security headers (e.g., `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`, `Content-Security-Policy`). This could expose the application to clickjacking, MIME-type sniffing, and other injection attacks if expanded.
**Learning:** Even internal or simple health endpoints should apply standard security headers, as they can act as vectors for subtle vulnerabilities or might be exposed unintentionally.
**Prevention:** Apply an `@app.after_request` hook that injects these headers uniformly across all responses.
