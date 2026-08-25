## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-24 - Prevent Credential Leakage in CLI Tool Output
**Vulnerability:** The CLI tool logged the full requested URL, which can inadvertently contain inline HTTP basic authentication credentials (e.g. `http://user:password@example.com/`). This would leak passwords directly into standard output, terminal histories, and CI run logs.
**Learning:** Any tool that handles user-provided or config-provided URLs must sanitize or mask those URLs before printing them to the console or log files. Simple string replacement or ignoring the issue relies on user perfection, which is fragile.
**Prevention:** Use standard URL parsing libraries (like `urllib.parse`) to detect password components in URLs and proactively mask them (e.g. `user:***@example.com`) before any diagnostic printing or logging occurs.
