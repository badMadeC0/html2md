import socket
import ipaddress
from urllib.parse import urlparse

url = "http://[::1]/"
parsed = urlparse(url)
print(parsed.hostname)
try:
    ip = socket.gethostbyname(parsed.hostname)
    print(ip)
except Exception as e:
    print(type(e), e)
