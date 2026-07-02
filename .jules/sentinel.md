## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-07-02 - Added HTTP Security Headers
**Vulnerability:** Missing security headers on Flask endpoints exposing the app to potential Clickjacking, MIME-sniffing and cross-site scripting (XSS) risks.
**Learning:** Even simple APIs and diagnostic endpoints like `/health` should implement defense-in-depth measures via standard HTTP response headers to limit exposure.
**Prevention:** Always implement a global hook (e.g. `@app.after_request`) in Flask applications to inject standard security headers like `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, and `Content-Security-Policy`.
