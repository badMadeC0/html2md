## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-08-02 - Sanitized URLs to Prevent Credential Leakage in Logs
**Vulnerability:** The CLI was printing the raw target URL directly to the console (`print(f"Processing URL: {target_url}")`). If a user provided a URL containing basic authentication credentials (e.g., `http://user:pass@example.com`), those credentials would be leaked in standard output.
**Learning:** URLs often contain sensitive information like basic auth credentials or tokens in the query string. Logging raw URLs without sanitization is a common vector for credential leakage.
**Prevention:** Always parse untrusted or user-provided URLs and strip or mask sensitive components (like `username` and `password`) before printing or logging them to any output stream. Use `urlunparse` to rebuild a safe display string.
