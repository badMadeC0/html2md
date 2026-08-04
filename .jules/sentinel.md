## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-08 - Prevent Cleartext Credentials in CLI Output
**Vulnerability:** The CLI printed URLs directly using `target_url`, exposing embedded basic authentication passwords to standard output (CWE-312 / CWE-532).
**Learning:** Even benign logging can be an exposure vector for sensitive data.
**Prevention:** Mask any credentials in URLs before passing them to `print()` or logging functions, e.g. using `urllib.parse`.
