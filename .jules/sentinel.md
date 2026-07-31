## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-07-31 - Add Flask Security Headers and Remove shell=True
**Vulnerability:** Flask application lacked standard security headers, exposing users to cross-site attacks and unencrypted connections. Additionally, `subprocess.run` used `shell=True` with string-based commands in tests, risking shell injection.
**Learning:** Default Flask apps do not include CSP, HSTS, or X-Frame-Options headers. Furthermore, `0.0.0.0` binds expose local apps to the network unnecessarily. Even in tests, `shell=True` is an anti-pattern.
**Prevention:** Use `@app.after_request` to inject standard security headers. Default local binds to `127.0.0.1`. Always use `shell=False` and pass arguments as lists in `subprocess`.
