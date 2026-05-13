## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-13 - Added XSS Sanitization to Markdown Generation
**Vulnerability:** The CLI was converting HTML directly to Markdown without sanitizing dangerous URI schemes (`javascript:`, `vbscript:`, `data:text/html`). If the resulting Markdown is viewed in an insecure renderer, this leads to Cross-Site Scripting (XSS).
**Learning:** Even when converting formats, the destination format (Markdown) can still carry execution payloads from the source format (HTML). Content conversion tools must assume the source material is malicious.
**Prevention:** Sanitize the input HTML using a robust parser (like BeautifulSoup) to strip or neuter dangerous attributes *before* performing the conversion to the target format.
