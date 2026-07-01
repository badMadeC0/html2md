## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since requests.get without stream=True buffers the entire response in memory.
**Prevention:** Always use stream=True when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2026-07-01 - Prevent URL Password Leak in CLI Output
**Vulnerability:** URLs containing basic auth credentials (e.g., http://user:password@example.com) leaked the password in plaintext when printed to stdout during processing and stderr during exceptions (requests.RequestException).
**Learning:** External libraries like 'requests' often embed the target URL in their exception messages. Simply masking the URL in proactive logging is insufficient; all external exception strings that might contain the URL must also be sanitized before printing.
**Prevention:** Always parse untrusted URLs using urlparse and mask the password property before logging. Catch exceptions from network/fetching libraries and sanitize the exception string if it might contain the credentialed URL.
