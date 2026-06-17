## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-06-17 - Added SSRF Protection to CLI

**Vulnerability:** The CLI fetched remote URLs without checking if they resolved to internal, private, loopback, or unspecified IP addresses. This allowed a Server-Side Request Forgery (SSRF) attack where a malicious URL could force the CLI to make requests to internal services that it should not have access to (e.g. `http://localhost/admin`, `http://169.254.169.254/latest/meta-data/`).

**Learning:** URL fetch tools must not implicitly trust DNS resolution for user-provided URLs. The DNS resolution should happen before the connection is established to ensure the target IP is safe to access, or the HTTP client itself should be configured to reject internal IP addresses. Even after resolving and checking the IP before the `get` call, a Time-of-Check to Time-of-Use (TOCTOU) DNS rebinding vulnerability still theoretically exists since `requests.get()` will perform its own DNS resolution again.

**Prevention:** Always extract the hostname from a user-provided URL and resolve it to an IP address using `socket.getaddrinfo`. Check this IP using `ipaddress` against private, loopback, link-local, multicast, and unspecified ranges before proceeding. For an even stronger defense against DNS rebinding, consider overriding the HTTP adapter or using an underlying connection that connects directly to the pre-validated IP address instead of passing the hostname again to `requests`.
