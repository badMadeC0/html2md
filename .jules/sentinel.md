## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-09 - Added Request Duration Limits to Prevent Slowloris DoS
**Vulnerability:** The CLI fetched remote URLs directly into memory in chunks, enforcing a total size limit, but without capping the duration of the entire download loop. A malicious or misconfigured server returning data at an extremely slow rate (e.g., 1 byte every 29 seconds) would keep the connection open indefinitely, creating a Denial of Service (DoS) vulnerability via a "Slow Read" or Slowloris attack.
**Learning:** Limiting response size is insufficient to prevent resource exhaustion. If the response streams indefinitely but very slowly, the connection and associated resources stay occupied. A global timeout on the streaming block is required.
**Prevention:** Always enforce a strict upper limit on the overall duration of the download, in addition to tracking total byte size limit.
