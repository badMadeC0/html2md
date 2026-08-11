## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-08-11 - Fixed SSRF vulnerability in the URL processing CLI
**Vulnerability:** The `html2md` CLI accepted URLs and fetched them using `requests.get` without checking if the resolved IP address belonged to a private, loopback, or link-local range. This creates a Server-Side Request Forgery (SSRF) vulnerability.
**Learning:** Even simple CLI fetching tools are susceptible to SSRF if the inputs are not validated. Internal endpoints such as AWS Metadata (169.254.169.254) or localhost API servers could be queried.
**Prevention:** Always extract the hostname from user-provided URLs and validate the resolved IP address against restricted IP ranges (like loopback, private, and link-local) before performing network requests.
