## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-07-25 - Prevent URL Password Leaks in CLI output
**Vulnerability:** The CLI fetched remote URLs and printed them directly to standard output and exception tracebacks (e.g., standard error). Since it accepted basic auth credentials within the URL (e.g., `http://user:password@example.com`), it leaked sensitive data.
**Learning:** Never assume URLs are safe to print as-is. They may contain credentials, tokens, or PII. `requests.RequestException` strings and stdout both need sanitization.
**Prevention:** Use `urllib.parse.urlparse` to identify if `parsed.password` exists, and mask it by replacing the password component before displaying it or logging it.
