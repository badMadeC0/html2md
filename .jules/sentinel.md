## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2026-05-15 - Added Security Headers to Flask App
**Vulnerability:** The Flask app in `src/html2md/app.py` was missing essential security headers (CSP, HSTS, X-Frame-Options, X-XSS-Protection, X-Content-Type-Options).
**Learning:** By default, Flask does not include standard security headers. These must be added explicitly to mitigate XSS and content-sniffing vulnerabilities.
**Prevention:** Added an `@app.after_request` hook to append security headers on all responses.
