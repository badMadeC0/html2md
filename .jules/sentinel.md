## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Prevented URL Password Leak in CLI Logging and Filenames
**Vulnerability:** The application accepted URLs with credentials (`http://user:pass@example.com`) and subsequently logged the raw URL and used it to generate file paths, leaking the plaintext password to the console output and filesystem.
**Learning:** Utilities that parse and log user input strings like URLs must sanitize sensitive components (like credentials) before outputting or using them to derive filenames.
**Prevention:** Mask sensitive parts of URLs (e.g. `password`) upon entry by creating helper functions like `_mask_url_password` and use these sanitized URLs for logging and string derivation.
