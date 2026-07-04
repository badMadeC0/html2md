## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-05-18 - Added Basic SSRF Protection for CLI URLs
**Vulnerability:** The CLI fetched remote URLs directly, making it susceptible to Server-Side Request Forgery (SSRF) if deployed in a server environment where users could supply URLs like `http://169.254.169.254` or `http://localhost`.
**Learning:** Checking the parsed hostname using `socket.gethostbyname` misses IPv6 addresses (e.g., `[::1]`) since it raises a `socket.gaierror`. Using `socket.getaddrinfo` ensures we correctly block IPv6 loopback and private addresses. Even so, this provides a defense-in-depth layer and remains vulnerable to DNS Rebinding TOCTOU since `requests` does its own resolution.
**Prevention:** Always use `socket.getaddrinfo` instead of `socket.gethostbyname` for validating host IPs, and explicitly reject loopback, link-local, and private addresses.
