## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-06-13 - Prevent Credential Leakage in CLI Output
**Vulnerability:** The CLI prints processed URLs and raw exception messages to `stdout`/`stderr` without sanitization. If a user provides a URL containing Basic Authentication credentials (e.g., `http://admin:secret@example.com`), the password is leaked in the console output and logs. Network error messages from `requests` often include the request URL, causing secondary leakage.
**Learning:** Any user-provided URL or raw exception message from an HTTP client may contain embedded credentials and must be considered sensitive data that should not be exposed in logs or console output.
**Prevention:** Implement a global string sanitization function (`_sanitize_text`) using regex to redact passwords from URLs (e.g., `http://admin:***@...`) before any output is logged or printed. Apply this to both informational messages and exception strings.
