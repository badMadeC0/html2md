## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-05-11 - Add Rate Limiting, SSRF Protection, and Security Headers
**Vulnerability:** The CLI was susceptible to Server-Side Request Forgery (SSRF), particularly DNS Rebinding and targeting Cloud Metadata endpoints (e.g., `169.254.169.254`). The Flask app was also missing rate limiting and common security headers (X-Frame-Options, HSTS, CSP).
**Learning:** For SSRF protection, using `socket.gethostbyname` is insufficient because it only handles IPv4 and ignores IPv6 (e.g. `[::1]`). Always use `socket.getaddrinfo` to resolve all IP versions. In-memory IP tracking for rate-limiting can cause a memory leak if inactive IPs are not evicted. Also, when adding new global state, test isolation (e.g., clearing the dictionary via Pytest fixtures) is critical to prevent cascading test failures. Finally, always check `is_link_local` alongside `is_private` and `is_loopback` to fully secure environments against metadata exfiltration.
**Prevention:**
- Use `@app.after_request` for global headers.
- Build clean-up hooks (`@app.teardown_request`) to manage memory.
- Check all IPs associated with a hostname against a comprehensive list of unsafe spaces (`is_private`, `is_loopback`, `is_link_local`).
- Use Pytest fixtures to clean up global module state between test runs.
