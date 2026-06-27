## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-06-27 - Added HTML Sanitization Before Markdown Conversion
**Vulnerability:** The CLI converted fetched HTML into Markdown without first sanitizing malicious elements. Tags like `<script>` or `<style>`, and attributes like `href="javascript:..."` were carried over to the Markdown output. This exposed consumers of the Markdown (like Previewers) to XSS (Cross-Site Scripting) or malicious code execution vectors.
**Learning:** Even when converting to a simpler format like Markdown, underlying conversion libraries (`markdownify`) may pass through malicious web elements unmodified. Markdown must be treated as a potential execution context if it is rendered later.
**Prevention:** Always use an HTML parser (like `BeautifulSoup`) to decompose dangerous tags (`script`, `style`, `iframe`, `object`, `embed`) and sanitize dangerous URI schemes (`javascript:`, `vbscript:`, `data:`) *before* invoking format conversion libraries.
