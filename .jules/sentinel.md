## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Prevented Credential Leakage in Logs and Error Messages
**Vulnerability:** The CLI printed raw URLs to stdout during normal execution and to stderr upon network exceptions. URLs containing HTTP Basic Auth credentials (e.g., `http://user:pass@example.com`) leaked plain text passwords to the terminal output and potential CI/CD logs.
**Learning:** Standard print statements and exception stringification do not automatically sanitize sensitive components of user input.
**Prevention:** Always parse URLs (e.g., `urllib.parse.urlparse`) and explicitly redact passwords before logging or echoing URLs to standard output or error streams.
