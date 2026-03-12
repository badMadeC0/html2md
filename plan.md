1. **Explore the codebase for security issues**
   - Look at `src/html2md/cli.py` which takes URL inputs and fetches them using the `requests` library.
   - Investigate potential SSRF (Server-Side Request Forgery) vulnerability. The application takes arbitrary URLs and fetches them via `requests.get`. If a user supplies a URL like `http://169.254.169.254/latest/meta-data/` or `http://localhost:8080/admin`, the application might fetch it and return the content, potentially leaking sensitive information from the internal network.
   - We should add validation to restrict fetching to external IP addresses.

2. **Implement SSRF Protection in `src/html2md/cli.py`**
   - Create a function to resolve the hostname and check if it's a public IP address or an internal/private one.
   - Use `socket.gethostbyname` to get the IP.
   - Use `ipaddress.ip_address` to check if the IP is private (`is_private`), loopback (`is_loopback`), etc.
   - Restrict fetching if the IP is determined to be non-public.
   - We must also consider DNS rebinding. While doing this in Python, the best way without a custom requests adapter is to resolve the IP, check it, and then make the request using the resolved IP and a Host header, or just accept the limitation. However, adding basic SSRF protection to block local network requests is a good start.

3. **Verify tests**
   - Make sure no existing tests are broken.
   - Write a new test to confirm SSRF protection works.

4. **Record learnings in `.jules/sentinel.md`**
   - Note the SSRF vulnerability in the `cli.py` script.
