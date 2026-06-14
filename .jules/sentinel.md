## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2026-06-14 - Flask Security Headers
**Vulnerability:** Missing basic security headers in Flask API
**Learning:** The Flask API lacked defense-in-depth headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options).
**Prevention:** Use `@app.after_request` to globally attach these headers to all responses.
