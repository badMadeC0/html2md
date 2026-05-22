## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2025-05-22 - [Slow-Read DoS during Streaming]
**Vulnerability:** A Slow-Read DoS vulnerability was identified when using streaming downloads (`requests.get(..., stream=True)` and `response.iter_content`). Although `timeout=30` was set on the request, this only applies to the *socket* timeout (time between bytes) and not the *absolute* time. An attacker could send data very slowly, at a rate just above the socket timeout, keeping the connection open indefinitely and exhausting server/client resources.
**Learning:** `requests.Session.get` socket timeout does not prevent Slowloris attacks during `iter_content`. When downloading files, particularly un-sized ones or ones from untrusted servers, an absolute timeout is necessary to ensure the application does not hang forever.
**Prevention:** Track the `start_time = time.time()` before the chunk reading loop, and inside the loop check if `time.time() - start_time > MAX_ALLOWED_TIME`. If it exceeds the time, terminate the connection and error out.
