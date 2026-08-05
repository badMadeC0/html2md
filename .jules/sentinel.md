## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2025-02-18 - Prevent Slow-Read DoS in streaming responses
**Vulnerability:** Slow-Read DoS (Denial of Service) when using requests.get(stream=True) because timeout only applies to connection, not total download.
**Learning:** Malicious servers can trickle data 1 byte at a time to tie up resources indefinitely.
**Prevention:** Always implement an absolute timeout check (e.g. comparing time.time() against a limit) inside the chunk reading loop when using stream=True.
