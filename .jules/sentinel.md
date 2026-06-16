## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-06-16 - Prevent Credential Leakage in URL Logging and File Generation
**Vulnerability:** The CLI accepted URLs containing Basic Auth credentials (e.g., `http://admin:secret@example.com/`) and directly echoed the raw URL to stdout during processing. Furthermore, when generating an output filename, it split the raw URL by `?`, leaving the credentials intact in the generated filename (e.g., `admin:secret@example.com.md`), writing credentials to the filesystem and potentially exposing them.
**Learning:** Raw URLs should never be used directly for logging or filename generation, as they may contain embedded sensitive data like credentials.
**Prevention:** Always parse URLs (e.g., with `urllib.parse.urlparse`) and explicitly extract/sanitize components. Mask `parsed.password` in logs and use `parsed.path` or `parsed.hostname` for generating local resource names.
