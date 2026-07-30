from markdownify import markdownify as md
html = "<html><body><h1>Hello</h1><script>alert(1)</script></body></html>"
print(md(html))
