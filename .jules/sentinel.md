## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Flask Security Headers & Stack Trace Prevention
**Vulnerability:** The Flask application endpoints lacked standard security headers, increasing risk for MIME-sniffing and clickjacking. Additionally, unhandled exceptions in the CLI tools (`upload.py`) would print verbose stack traces to standard error, potentially leaking implementation details.
**Learning:** Even simple APIs need basic security headers (`X-Frame-Options`, `Content-Security-Policy`, etc.). CLI tools must intercept all exceptions before they reach the interpreter's default unhandled exception hook to prevent information leakage.
**Prevention:** Use `@app.after_request` in Flask to inject security headers on all responses, and wrap CLI entry points in a broad `try...except Exception` block with a generic error message.
