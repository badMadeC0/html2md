## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Mask Basic Auth Passwords in Logs
**Vulnerability:** The CLI prints the full, raw target URL to stdout when processing. If the URL contains basic authentication credentials (e.g., `https://user:password@example.com`), the password is leaked to terminal output or CI logs.
**Learning:** Raw inputs containing connection strings, URLs, or other connection details often embed credentials. Directly logging these variables without sanitization is a common credential exposure vector.
**Prevention:** Always parse URLs (e.g., using `urllib.parse.urlparse`) and replace sensitive components like `.password` with mask characters (e.g., `***`) before printing or logging them.
