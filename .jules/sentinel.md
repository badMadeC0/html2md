## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2026-06-24 - [MEDIUM] Add security headers to Flask app
**Vulnerability:** The Flask application was missing standard security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Strict-Transport-Security`), leaving it vulnerable to attacks such as clickjacking and MIME-type sniffing.
**Learning:** For a minimal API, basic headers provide defense in depth and should be added globally, especially to prevent browser-side exploitation.
**Prevention:** Implement an `@app.after_request` hook that applies these standard security headers to all responses. Set CSP to `default-src 'none'` for pure API endpoints.
