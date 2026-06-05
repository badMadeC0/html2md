## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Prevented Credential Leaks in URL Logging
**Vulnerability:** The CLI tool directly logged input URLs to stdout and embedded them in error messages. If a user provided a URL with basic authentication credentials (e.g., `http://admin:secret@example.com/`), the password would be printed to the console or log file, exposing the secret.
**Learning:** Raw user inputs, particularly URLs, can contain embedded secrets. These must be sanitized before logging or including in exception messages.
**Prevention:** Always parse and sanitize URLs to mask credentials (e.g., replacing passwords with `***`) before logging them or injecting them into error messages.
