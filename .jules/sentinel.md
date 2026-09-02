## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-24 - Added Content-Type Validation to Prevent ReDoS and Resource Exhaustion
**Vulnerability:** The CLI fetched remote URLs up to 10MB in size and decoded them as text without verifying the `Content-Type`. If an attacker provided a URL pointing to a 10MB binary file (e.g., an image or ISO), the application would attempt to decode the binary data as UTF-8 (using error replacement) and pass the resulting massive, complex string to the Markdown parser (`markdownify`/`beautifulsoup`). This could lead to a Denial of Service (DoS) through severe CPU exhaustion (ReDoS or algorithmic complexity attacks in the parsers).
**Learning:** Limiting response size is only half the battle. Passing large, unstructured, binary-derived garbage strings to complex HTML/Markdown parsers is dangerous and can lead to excessive resource consumption.
**Prevention:** Always validate the `Content-Type` header (e.g., ensuring it is `text/*` or `application/xhtml+xml`) before reading and passing remote responses to parsers.
