## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-10-26 - Sanitized credentials in logged URLs
**Vulnerability:** The CLI logged the exact URL being processed, including any basic authentication credentials, leading to password leakage in plaintext on stdout.
**Learning:** Basic authentication credentials provided in URLs must be sanitized before being logged or printed.
**Prevention:** Use `urllib.parse` to identify if a URL contains a password, and sanitize it using `_replace` to mask the password before logging it.
