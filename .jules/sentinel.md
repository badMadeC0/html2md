## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-05-18 - Added Security Headers to Flask App
**Vulnerability:** The Flask application was missing standard HTTP security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options), which could leave it vulnerable to clickjacking, sniffing, and XSS if expanded in the future.
**Learning:** Even simple healthcheck APIs benefit from defense-in-depth security headers, ensuring a secure-by-default posture as the application grows.
**Prevention:** Implement an `@app.after_request` middleware in Flask to uniformly apply security headers to all responses.
