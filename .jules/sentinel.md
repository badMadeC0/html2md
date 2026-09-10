## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.

## 2024-05-24 - Added Server-Side Request Forgery (SSRF) Protection to URL Fetcher
**Vulnerability:** The CLI fetched remote URLs directly into memory without checking if the resolved IPs were public or private. This allowed attackers to perform SSRF attacks by pointing the CLI at internal addresses (e.g. `127.0.0.1`, `169.254.169.254`, `10.x.x.x`), potentially scanning internal networks or leaking sensitive internal metadata.
**Learning:** Tools that fetch user-supplied URLs must validate that the target IP address is publicly routable before initiating a network request. This is particularly important for tools deployed as services, or those running on CI/CD pipelines with access to internal network resources.
**Prevention:** Implement an `is_internal_url` check leveraging `socket.gethostbyname` and `ipaddress` module to reject any URLs resolving to private, loopback, link-local, or multicast IPs before fetching.
