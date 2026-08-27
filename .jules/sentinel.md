## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2026-08-27 - Added SSRF Protection to CLI Requests
**Vulnerability:** The CLI fetched remote URLs via `requests.get` without any Server-Side Request Forgery (SSRF) mitigations. This meant an attacker could supply URLs pointing to internal or private resources (e.g., `localhost`, `127.0.0.1`, AWS metadata `169.254.169.254`, or `10.x.x.x`), potentially scanning or accessing sensitive internal endpoints.
**Learning:** Tools making outbound HTTP requests must validate the resolved IP address to prevent SSRF and DNS rebinding (TOCTOU) attacks, rather than just checking the initial hostname.
**Prevention:** Implement a custom `HTTPAdapter` for `requests` that resolves the hostname, checks if the resulting IP is private/loopback/link-local/unspecified, blocks disallowed IPs, and rewrites the connection to use the verified IP (to mitigate TOCTOU DNS rebinding).
