## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-06-22 - [Critical] SSRF Vulnerability in CLI Fetching Logic
**Vulnerability:** The CLI fetched URLs using `requests.get()` without verifying if the resolved IP address was internal or private.
**Learning:** URL fetchers that accept user input are highly susceptible to Server-Side Request Forgery (SSRF) if they don't validate the resolved IP. The `urllib.parse` does not provide IP context, so DNS resolution using `socket.getaddrinfo` paired with `ipaddress.ip_address` to check `is_private`, `is_loopback`, and `is_link_local` properties is required to protect against requests reaching internal services.
**Prevention:** Implement an IP resolution check *before* passing the URL to the HTTP client (e.g. `requests.get()`).
