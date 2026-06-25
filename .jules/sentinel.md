## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2025-02-25 - Credential Leakage in URL Logging
**Vulnerability:** Passwords embedded in standard URLs (e.g., `https://user:password@example.com/`) were printed to standard output during the fetching initialization phase in the CLI.
**Learning:** Raw URLs processed from command line inputs or files should be explicitly parsed and sanitized before being outputted, logged, or included in error messages, as users might pass connection strings containing credentials directly.
**Prevention:** Use standard parsing libraries (like `urllib.parse.urlparse`) to inspect the components of a URL and redact `password` if present (e.g., using `urlparse` and replacing the `netloc` component) before passing the string to any logging or print function.
