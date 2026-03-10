import os
import sys

target_url = "http://example.com/../../etc/passwd"
outdir = "/tmp/out"
url_path = target_url.split('?')[0].rstrip('/')
if url_path:
    base = os.path.basename(url_path)
    if base:
        filename = f"{base}.md"

out_path = os.path.join(outdir, filename)
print(out_path)
