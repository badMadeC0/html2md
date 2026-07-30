## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## $(date +%Y-%m-%d) - Added Security Headers to Flask API
**Vulnerability:** The Flask application lacked standard security headers, leaving it potentially vulnerable to MIME sniffing, clickjacking, and XSS if future endpoints were added or if browsers misbehaved.
**Learning:** Even pure JSON APIs should include defense-in-depth security headers like `Content-Security-Policy: default-src 'none'` to restrict browsers from interpreting responses as HTML/scripts if an endpoint ever leaks user input.
**Prevention:** Always use an `@app.after_request` hook in Flask to enforce strict default security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, and `Strict-Transport-Security`) across all API responses.
