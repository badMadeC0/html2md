## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-08 - Prevent XSS in Markdown Output
**Vulnerability:** The CLI converted HTML to Markdown without stripping potentially dangerous tags (like `<script>`, `<style>`, `<iframe>`, `<object>`, and `<embed>`). While Markdown itself doesn't execute these tags, rendering the resulting Markdown output in an insecure web viewer could lead to Stored XSS if malicious scripts are preserved as plain HTML within the Markdown.
**Learning:** HTML-to-Markdown conversion can silently pass XSS payloads into the Markdown artifact unless explicitly sanitized. Default conversions often preserve unknown tags or their contents.
**Prevention:** Explicitly sanitize HTML by decomposing potentially dangerous tags (e.g. using BeautifulSoup) prior to passing the HTML into the markdown converter.
