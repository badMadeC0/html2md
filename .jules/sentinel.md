## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-18 - Added Security Headers to Flask Application
**Vulnerability:** The Flask application endpoints lacked standard security HTTP response headers. This could expose the application to content sniffing, clickjacking, and lack of strict transport security.
**Learning:** Security headers should be injected universally across all endpoints using an `after_request` hook or middleware in a web framework rather than doing it manually for each endpoint.
**Prevention:** Configure a default `after_request` hook in the Flask app to apply headers like `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`, and `Content-Security-Policy` to all outgoing responses.
