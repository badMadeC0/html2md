## 2024-05-18 - Unbounded HTTP Response Handling (DoS)
**Vulnerability:** The CLI fetched HTTP content using `requests.get()` without `stream=True` and passed `response.text` directly into the parser. This allowed a malicious server to keep the connection open and stream an infinite amount of data, causing resource exhaustion (OOM) and DoS on the client.
**Learning:** `requests.get()` buffers the entire response in memory by default. When downloading content from untrusted external URLs, failure to impose length constraints can break the client application.
**Prevention:** Always use `stream=True` on `requests.get()` when dealing with external content, and use `iter_content()` with a maximum total byte counter (e.g., 10MB limit) to safely bound the amount of data read into memory.
