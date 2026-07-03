## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-05-09 - Prevent URL Credentials from Leaking in Logs and Filenames
**Vulnerability:** The CLI application processed URLs that could contain basic authentication credentials (e.g., `http://user:password@example.com`). The application printed `print(f"Processing URL: {target_url}")` directly, exposing plaintext passwords to console logs. Furthermore, the auto-generated filename could inadvertently extract the credentials into the `.md` output filename.
**Learning:** URL manipulation functions like `urllib.parse.urlparse` correctly extract passwords, but the original URL structure may still be used inadvertently for console output and logging.
**Prevention:** Mask passwords explicitly in logged URLs, and safely reconstruct target URLs for output paths so that credentials are omitted entirely from artifacts.
