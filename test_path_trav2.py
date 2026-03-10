import os

target_url = "http://example.com/../../etc/passwd"
outdir = "output"
filename = "conversion_result.md"
url_path = target_url.split('?')[0].rstrip('/')
if url_path:
    base = os.path.basename(url_path)
    if base:
        filename = f"{base}.md"

out_path = os.path.join(outdir, filename)
print(out_path)
