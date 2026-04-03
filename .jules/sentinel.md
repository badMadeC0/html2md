## 2024-04-03 - [MEDIUM] Add input length limits to prevent DoS
**Vulnerability:** The CLI was downloading files by reading the entire response body into memory at once (`session.get(target_url)`), leaving it vulnerable to Out-Of-Memory (OOM) / Denial of Service (DoS) attacks if a malicious server returned an endless or massive payload.
**Learning:** In python scripts dealing with external URLs, always use stream processing and size limits, as malicious payload sizes can crash memory.
**Prevention:** Use `stream=True` in `requests.get` and process content in chunks, explicitly tracking accumulated size and terminating the request if it exceeds reasonable bounds (e.g., 10MB).
