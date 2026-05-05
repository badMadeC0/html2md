## 2024-05-05 - Identify SSRF Risk
**Vulnerability:** Found a Server-Side Request Forgery (SSRF) risk in `html2md.cli` due to fetching arbitrary URLs from user input.
**Learning:** Tools that fetch user-provided URLs can inadvertently expose internal network services or metadata endpoints.
**Prevention:** Sanitize and restrict the host names and IP addresses before making network requests.
