## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-03-22 - Credential Leak in URL Logging
**Vulnerability:** The CLI was printing the target URL directly using `print(f"Processing URL: {target_url}")` before fetching it. If a user provided a URL with embedded credentials (e.g., `http://user:pass@example.com`), those credentials would be printed in plain text to the console, risking exposure in logs or terminal history.
**Learning:** Always treat user-provided URLs as potentially containing sensitive data. Logging or printing raw URLs without sanitization can inadvertently leak credentials.
**Prevention:** Use URL parsing libraries (like `urllib.parse.urlparse`) to inspect and sanitize URLs, stripping out `username` and `password` components before logging or displaying them.
