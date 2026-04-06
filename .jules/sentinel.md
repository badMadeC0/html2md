## 2026-04-06 - [SSRF Protection]
**Vulnerability:** The `html2md` CLI accepted arbitrary URLs via `--url` or `--batch` without validating the hostname, exposing the application to Server-Side Request Forgery (SSRF). An attacker could fetch data from internal endpoints (like 127.0.0.1 or AWS metadata).
**Learning:** External URL fetching must validate hostnames against private/loopback/link-local/unspecified address ranges before performing requests, and must use `socket.getaddrinfo` to properly handle both IPv4 and IPv6 addresses.
**Prevention:** Added an `is_internal_url` helper function that resolves hostnames (supporting IPv4/IPv6) and checks against `ipaddress.is_private`, `is_loopback`, `is_link_local`, and `is_unspecified`. Always place this check before calling `requests.get()`.
