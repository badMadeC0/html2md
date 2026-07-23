## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-08 - Flask Security Headers Enhancement
**Vulnerability:** The Flask application lacked default security headers, which are essential for defense in depth.
**Learning:** Default security headers such as `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, and `Strict-Transport-Security` should always be present to mitigate a class of client-side vulnerabilities.
**Prevention:** Apply a global response hook (e.g., `@app.after_request` in Flask) to inject these headers into all HTTP responses.
