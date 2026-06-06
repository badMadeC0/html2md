## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Prevent Server-Side Request Forgery (SSRF) in URL fetching
**Vulnerability:** The CLI fetched URLs directly without checking if the resolved IP addresses point to internal, private, or loopback network addresses, which allows Server-Side Request Forgery (SSRF).
**Learning:** In URL fetching utilities, user-provided URLs can resolve to sensitive internal addresses (e.g., localhost, AWS metadata, etc), and following redirects blindly could also lead to similar vulnerabilities.
**Prevention:** Use `socket.getaddrinfo` to resolve hostnames before making HTTP requests and use `ipaddress` module to block any internal or unroutable IPs. Additionally, disable automatic redirects and manually validate the URL at each redirect step.
