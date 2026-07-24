## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-07-24 - Prevent Credential Leakage in CLI Output
**Vulnerability:** The CLI printed the target URL directly to stdout during processing, and also logged full exception string representations to stderr. If a user provided a URL with embedded Basic Auth credentials (e.g., `http://user:pass@example.com`), these credentials would be leaked to the terminal and any error logs.
**Learning:** CLI tools often echo user input or raw exception messages to the console. When handling URLs, this can inadvertently expose embedded secrets. It's critical to sanitize URLs before displaying them or their associated error messages.
**Prevention:** Apply a robust sanitization function (e.g., using regex to replace `user:pass` in `http://user:pass@...` with `***:***`) to all URLs printed to output and to all exception messages converted to strings before printing.
