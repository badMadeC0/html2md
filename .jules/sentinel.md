## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2025-02-28 - Added XSS Mitigation for Rendered Markdown
**Vulnerability:** The CLI fetched remote HTML pages and directly converted their content to Markdown using `markdownify`, preserving potentially malicious URL schemes like `javascript:`, `vbscript:`, and `data:` in `href` and `src` attributes. When the generated Markdown is rendered by standard Markdown viewers, these payloads could execute Cross-Site Scripting (XSS).
**Learning:** Tools that convert external HTML to Markdown must sanitize the HTML before conversion, as Markdown renderers often trust the underlying schemes for links and images. An attacker controlling a page being converted could inject persistent XSS into the generated Markdown document.
**Prevention:** Ensure that links and images with dangerous schemes (`javascript:`, `vbscript:`, `data:`) are sanitized out (replaced with safe fallbacks or removed) using a parser (e.g., `BeautifulSoup`) prior to Markdown conversion.
