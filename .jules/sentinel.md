## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2025-02-27 - Prevent URL Password Leakage in CLI Tools
**Vulnerability:** The CLI printed out raw input URLs in its logging and exception messages, exposing basic authentication passwords when URLs like `https://user:password123@example.com` were processed.
**Learning:** URL components (particularly credentials like `username:password`) are often overlooked when logging or printing raw input strings, causing sensitive data to be exposed in CI/CD logs, terminals, or exception traces.
**Prevention:** Always parse and sanitize URLs (e.g., using `urllib.parse`) to mask or remove password fields before displaying or logging them, even in error handling logic.
