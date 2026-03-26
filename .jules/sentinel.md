
## 2024-05-30 - Server-Side Request Forgery (SSRF) in URL Fetching
**Vulnerability:** The CLI application allowed any `http` or `https` URL to be fetched without validation, exposing the local network, metadata services (e.g., `169.254.169.254`), and loopback interface (`localhost`, `127.0.0.1`) to SSRF attacks.
**Learning:** This existed because the original implementation only validated the URL scheme and relied on the Python `requests` library to fetch the content. It failed to account for the fact that `requests` can follow local/private IPs and redirect traffic to internal networks.
**Prevention:** Implement a check that resolves the hostname to an IP address (`socket.getaddrinfo`) and explicitly blocks the request if the IP matches any `is_private`, `is_loopback`, `is_link_local`, `is_multicast`, `is_unspecified`, or `is_reserved` conditions using the `ipaddress` library.
