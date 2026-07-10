## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Prevented XSS in HTML-to-Markdown Conversion
**Vulnerability:** Converting HTML to Markdown using `markdownify` does not automatically sanitize dangerous URL schemes in `href` and `src` attributes (e.g., `javascript:`, `vbscript:`, `data:text/html`). This allows XSS payloads to be passed through to the generated Markdown. If the resulting Markdown is rendered in an unsafe viewer, the payloads can execute.
**Learning:** `markdownify` is a format converter, not an HTML sanitizer. Unsafe content in the HTML will often remain unsafe in the generated Markdown.
**Prevention:** Pre-parse the HTML using a parser like `BeautifulSoup` and explicitly strip attributes containing dangerous schemes before converting to Markdown.
