
## 2024-05-06 - Prevent Server-Side Request Forgery (SSRF) in URL Converter
**Vulnerability:** The application was directly fetching user-provided URLs using `requests.get` without restricting the hostname to public addresses. This could allow an attacker to bypass firewalls and access internal/private services (like `localhost:8080` or AWS metadata endpoint `169.254.169.254`).
**Learning:** Checking the URL scheme (http/https) is not enough to prevent SSRF. The underlying IP address must be resolved and validated before making network requests.
**Prevention:** Always parse the URL, resolve its hostname to an IP address (using `socket.getaddrinfo` to avoid DNS/CNAME tricks), and use the `ipaddress` module to ensure the resolved IP is not in a private, loopback, link-local, unspecified, or reserved range.
