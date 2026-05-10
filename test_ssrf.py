from urllib.parse import urlparse
import socket
import ipaddress

def check_ssrf(url):
    parsed = urlparse(url)
    try:
        hostname = parsed.hostname
        if hostname:
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                print(f"Blocked: {url} resolves to {ip}")
                return False
    except Exception as e:
        print(f"Failed to resolve {url}: {e}")
    print(f"Allowed: {url}")
    return True

check_ssrf("http://169.254.169.254/latest/meta-data/")
check_ssrf("http://localhost:8080/admin")
check_ssrf("http://127.0.0.1/")
check_ssrf("http://example.com")
check_ssrf("http://192.168.1.1")
check_ssrf("http://10.0.0.1")
