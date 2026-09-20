## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-09-20 - Prevented Processing of Binary Files to Avoid ReDoS and Resource Exhaustion
**Vulnerability:** The CLI was blindly downloading and passing any requested file (like `image/png`, `application/pdf`, etc.) to the HTML-to-Markdown parser as long as it was under the 10MB size limit. Attempting to decode binary files as UTF-8 and parsing them with BeautifulSoup and regexes can trigger ReDoS (Regular Expression Denial of Service) and excessive CPU/Memory consumption.
**Learning:** Checking the `Content-Length` header is insufficient for security if the content itself is malicious or triggers worst-case performance in the parser.
**Prevention:** Validate the `Content-Type` header from the HTTP response before processing, and explicitly reject known binary/unsupported mime types.
