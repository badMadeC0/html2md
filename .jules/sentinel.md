## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2026-05-21 - Added SSRF Protection to Prevent Internal Network Access
**Vulnerability:** The CLI fetched remote URLs directly using `requests.get` with transparent redirection. This exposed the application to Server-Side Request Forgery (SSRF), allowing an attacker to fetch metadata (like `169.254.169.254`), loopback, or private internal network interfaces by providing an internal IP or setting up a server that redirects to one.
**Learning:** Naive HTTP clients automatically follow redirects and resolve hostnames blindly, bypassing basic string-matching URL checks.
**Prevention:** Always disable automatic redirects (`allow_redirects=False`) when fetching untrusted URLs. Manually handle redirects and validate the hostname's resolved IP address against restricted ranges (loopback, private, link-local) using `socket.getaddrinfo` and `ipaddress` before making any network call.
