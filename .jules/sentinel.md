## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Prevent Server-Side Request Forgery (SSRF) via Redirects
**Vulnerability:** The CLI fetched arbitrary URLs using `requests.get()` without restricting access to internal, loopback, or private IPs. Additionally, by automatically following redirects (`allow_redirects=True`), it allowed an attacker to bypass initial URL validation if a benign global URL redirected to an internal target (e.g. `http://169.254.169.254/`).
**Learning:** SSRF validation must occur on the resolved IP address of the target, and this validation must be applied to *every* step in a redirect chain, not just the initial request.
**Prevention:** Resolve hostnames to IPs using `socket.getaddrinfo` and block internal/private ranges using `ipaddress`. Handle redirects manually (`allow_redirects=False` in `requests.get`) to validate the `Location` header before following it.
