## 2025-02-23 - Prevent DoS via Large File Downloads
**Vulnerability:** The CLI application fetched URLs via `requests.get()` directly loading `response.text` into memory, making it vulnerable to resource exhaustion (DoS) when provided with URLs pointing to massive files (e.g. multi-gigabyte files).
**Learning:** For a CLI utility fetching user-supplied or unverified URLs, failing to limit download sizes can lead to out-of-memory errors and application crashes. Loading directly into `response.text` bypasses safe streaming.
**Prevention:** Use `stream=True` in `requests.get()`, check the `Content-Length` header upfront, and manually limit chunk sizes during `iter_content()`. Reassign the chunked bytearray to `response._content` to retain the native encoding detection of `requests`.
