## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-09-20 - Prevented Server-Side Request Forgery (SSRF) via Input URLs
**Vulnerability:** The CLI directly fetched external URLs using `requests.get` without validating the resolved IP address. This allowed an attacker to input URLs like `http://localhost/` or `http://169.254.169.254/` (cloud provider metadata) to scan internal services or access sensitive infrastructure behind the firewall.
**Learning:** Naively passing user-provided URLs to HTTP clients is a major risk. A hostname can be deceptive and resolve to internal addresses. Also, `socket.gethostbyname` does not support IPv6.
**Prevention:** Resolve the URL's hostname to an IP address (using `socket.getaddrinfo` to support both IPv4 and IPv6) before fetching, and explicitly block private, loopback, link-local, and multicast IP ranges using `ipaddress` to prevent SSRF attacks.
