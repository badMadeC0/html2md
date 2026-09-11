## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2026-09-11 - Fixed Unintended Network Exposure in Flask App
**Vulnerability:** The Flask application in `src/html2md/app.py` was defaulting to listen on `'0.0.0.0'` when no `HOST` environment variable was provided.
**Learning:** Binding to `'0.0.0.0'` exposes the application to all available network interfaces, which can lead to unintended access and potential exploitation if deployed without explicit host configuration.
**Prevention:** Always default to binding to localhost (`'127.0.0.1'`) to restrict access strictly to the local machine unless a different network interface is explicitly configured by the user or environment.
