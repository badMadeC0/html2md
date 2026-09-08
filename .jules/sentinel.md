## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Masked Passwords in URLs during Processing
**Vulnerability:** The CLI printed the full `target_url` directly when processing requests. If the URL contained Basic Auth credentials (e.g., `http://user:password@example.com`), the password was leaked in the console output and potentially CI logs.
**Learning:** Any logging or printing of user-provided URLs must account for embedded authentication credentials. Printing un-sanitized URLs represents a significant credential exposure risk.
**Prevention:** Use `urllib.parse.urlparse` to inspect URLs before printing. If `parsed.password` is present, use a replacement mechanism to mask the password (e.g., `:***@`) before sending it to the console or logs.
