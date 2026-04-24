with open(".github/workflows/request-jules-review.yml", "r") as f:
    content = f.read()

# Add pull-requests: write permission
if "pull-requests: write" not in content:
    content = content.replace("permissions:\n  issues: write\n", "permissions:\n  issues: write\n  pull-requests: write\n")

with open(".github/workflows/request-jules-review.yml", "w") as f:
    f.write(content)
