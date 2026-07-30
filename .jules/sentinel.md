## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2025-01-22 - Sanitize URL Inputs to Prevent Validation Bypasses
**Vulnerability:** URL scheme validation logic (`urlparse(url).scheme not in ("http", "https")`) could be bypassed because `urllib.parse.urlparse` allows certain leading characters like `\n`, `\r\n`, or spaces for otherwise forbidden schemes like `javascript:` and `file:`, treating them as valid.
**Learning:** `requests` depends on `urllib3` which might act differently when consuming un-sanitized URLs, which means `urlparse` might correctly or incorrectly handle leading spaces in ways that bypass the initial security gate while still triggering unintended requests.
**Prevention:** Always `strip()` un-trusted URLs to remove leading/trailing whitespaces and control characters prior to validating their schemes.
