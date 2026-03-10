import os
import urllib.parse
from pathlib import Path
url1 = "http://example.com/../../etc/passwd"

url_path = url1.split('?')[0].rstrip('/')
if url_path:
    base = os.path.basename(url_path)
    if base:
        filename = f"{base}.md"

print("Base:", base)
print("Filename:", filename)

safe_base = os.path.basename(urllib.parse.urlparse(url1).path)
print("Safe base:", safe_base)
