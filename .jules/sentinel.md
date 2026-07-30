## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-08 - Prevent URL Credentials Leakage in Output and Filenames
**Vulnerability:** HTTP Basic Auth credentials embedded in URLs (e.g., `http://user:pass@example.com`) were leaked to stdout during logging ("Processing URL: ...") and to the local filesystem when the URL was used to construct a default fallback filename (e.g., `user:pass@example.com.md`).
**Learning:** URL parsing (`urllib.parse`) correctly extracts credentials, but caution must be exercised when reconstructing or logging the URL. Reconstructing `parsed.netloc` while avoiding properties that strip formatting (like IPv6 brackets via `hostname`) or raise exceptions (like non-numeric ports via `port`) is necessary for a robust redaction implementation.
**Prevention:** Mask sensitive parts of the URL (like passwords) early before they reach any logging, telemetry, or storage functions, ensuring formatting parity across edge cases like IPv6 or invalid ports.
