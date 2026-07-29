## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Fix Credential Leak in Auto-generated Filenames
**Vulnerability:** The CLI auto-generated filenames from URLs by string manipulation without stripping the basic authentication part, leading to credentials leaking on disk as the filename.
**Learning:** Extracting filenames directly from raw URL strings using `.split('?')[0]` is dangerous since URLs might contain embedded basic auth credentials.
**Prevention:** Always use safe parsed structures like `urllib.parse.urlparse` and extract paths or hostnames, ignoring embedded credentials, when constructing paths. Ensure cross-platform safety by replacing colons `replace(':', '_')` as well.
