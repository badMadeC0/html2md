with open(".github/workflows/request-jules-review.yml", "r") as f:
    content = f.read()

content = content.replace("permissions:\n  issues: write", "permissions:\n  issues: write\n  pull-requests: write")

with open(".github/workflows/request-jules-review.yml", "w") as f:
    f.write(content)
