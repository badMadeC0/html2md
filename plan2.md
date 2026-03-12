1. **Analyze `cli.py`**
   - The CLI fetches URLs based on user input. It doesn't validate if the target is an internal IP. This is an SSRF vulnerability if the tool is run on a server (e.g., via a web app or an API).
   - The fix requires resolving the hostname, checking if it is an internal/private IP, and throwing an error if so.

2. **Implement SSRF Protection in `src/html2md/cli.py`**
   - Import `socket` and `ipaddress`.
   - In `process_url`, extract the hostname using `parsed.hostname`.
   - Resolve it using `socket.getaddrinfo(parsed.hostname, parsed.port)`.
   - Iterate through IPs. If any IP is private or loopback, raise an exception or print an error and return.
   - Example check:
     ```python
     import socket
     import ipaddress
     try:
         for res in socket.getaddrinfo(parsed.hostname, None):
             ip = ipaddress.ip_address(res[4][0])
             if ip.is_private or ip.is_loopback or ip.is_link_local:
                 print(f"Error: SSRF attempt blocked. URL resolves to an internal IP.", file=sys.stderr)
                 return
     except socket.gaierror:
         print(f"Error: Could not resolve hostname '{parsed.hostname}'.", file=sys.stderr)
         return
     except ValueError:
         pass
     ```
   - Insert this right after `if parsed.scheme not in ('http', 'https'):` check.

3. **Verify tests**
   - Make sure no existing tests are broken.
   - Add a test or update existing tests.

4. **Record learnings in `.jules/sentinel.md`**
   - Note the SSRF vulnerability in the `cli.py` script and the prevention strategy (IP checking).

5. **Submit changes**
   - Pre-commit checks.
   - Submit PR.
