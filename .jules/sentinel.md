## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-08-09 - Masked Passwords in Basic Auth URLs
**Vulnerability:** The CLI leaked Basic Authentication credentials by logging the raw URL to stdout during execution and embedding the raw URL in stringified exceptions printed to stderr upon network/file failure.
**Learning:** Python's standard `print()` combined with `urllib` representations don't automatically sanitize embedded credentials. Always manually sanitize input strings that reflect URLs if there is any possibility they contain credentials (e.g. `http://user:pass@example.com`).
**Prevention:** Use `urllib.parse.urlparse` to identify if a password exists in a URL and manually obscure it via `url.replace(f":{parsed.password}@", ":***@")` before logging, storing, or returning it in error messages.
