import urllib.parse
import ipaddress

def is_safe_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False

        # Try to parse as IP to block local/private IPs
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
                return False
        except ValueError:
            # Not an IP address, which is fine (could be example.com)
            # You might want to resolve it and check the IP, but that adds overhead.
            # At minimum, block obvious localhost
            if hostname.lower() in ('localhost', 'localhost.localdomain', '0.0.0.0'):
                return False
        return True
    except Exception:
        return False

print(is_safe_url("http://169.254.169.254/latest/meta-data/"))
print(is_safe_url("http://127.0.0.1/admin"))
print(is_safe_url("http://localhost:8080"))
print(is_safe_url("http://example.com"))
