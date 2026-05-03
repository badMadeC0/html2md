with open(".github/workflows/gemini-code-assist.yml", "r") as f:
    content = f.read()

content = content.replace("uses: mock-gemini/code-assist-action@v1", "run: echo 'mock'")

with open(".github/workflows/gemini-code-assist.yml", "w") as f:
    f.write(content)
