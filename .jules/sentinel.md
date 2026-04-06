## $(date +%Y-%m-%d) - [SSRF Protection]
**Vulnerability:** The `html2md` CLI accepted arbitrary URLs via `--url` or `--batch` without validating the hostname, exposing the application to Server-Side Request Forgery (SSRF). An attacker could fetch data from internal endpoints (like 127.0.0.1 or AWS metadata).
**Learning:** External URL fetching must validate hostnames against private/loopback/link-local address ranges before performing requests.
**Prevention:** Added an `is_internal_url` helper function that resolves hostnames and checks against `ipaddress.is_private`, `is_loopback`, and `is_link_local`. Always place this check before calling `requests.get()`.
