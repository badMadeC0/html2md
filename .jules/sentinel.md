## 2024-04-25 - Prevent Memory Exhaustion DoS in HTTP Requests
**Vulnerability:** The CLI fetched full URL contents into memory using `requests.get` without streaming, which created a Denial of Service (DoS) risk if an endpoint returned an infinitely large response (e.g. tarballs, endless data streams).
**Learning:** Default HTTP client behavior in Python often reads the entire response body into memory at once. For unbounded or untrusted inputs, this is a significant availability and security risk.
**Prevention:** Use `stream=True` on `requests.get()` and read data in chunks (`iter_content`), enforcing a strict maximum size limit (e.g. 10MB) to abort immediately when exceeded.
