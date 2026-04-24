with open('.github/workflows/request-jules-review.yml', 'r') as f:
    content = f.read()

# Add pull-requests: write permission
content = content.replace(
"""permissions:
  issues: write""",
"""permissions:
  issues: write
  pull-requests: write"""
)

with open('.github/workflows/request-jules-review.yml', 'w') as f:
    f.write(content)
