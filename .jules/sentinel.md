## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-08-21 - Added SSRF Protection
**Vulnerability:** The CLI fetched remote URLs using `requests.Session().get()` which allows fetching from private network space (like localhost, AWS metadata endpoints, etc).
**Learning:** `requests` will follow redirects, which can bypass simple upfront hostname checks. A malicious server can return a 302 redirect to a local or internal IP address, turning the CLI into a proxy for Server-Side Request Forgery (SSRF).
**Prevention:** Always perform IP resolution (e.g. `socket.gethostbyname`) and check against restricted ranges (e.g. `ipaddress.is_private`) *before* every single request in a redirect chain by handling redirects manually with `allow_redirects=False`.
