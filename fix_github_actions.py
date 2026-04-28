import re

# Fix 1: remove or comment out google-gemini/code-assist-action
file1 = ".github/workflows/gemini-code-assist.yml"
with open(file1, "r") as f:
    content1 = f.read()
# Comment it out because the repo doesn't exist anymore
content1 = content1.replace("uses: google-gemini/code-assist-action@v1", "# uses: google-gemini/code-assist-action@v1")
with open(file1, "w") as f:
    f.write(content1)

# Fix 2: fix the permissions in request-jules-review.yml
file2 = ".github/workflows/request-jules-review.yml"
with open(file2, "r") as f:
    content2 = f.read()

# For a PR from a fork (or default token permissions), the token might only have read access.
# Wait, github.event_name is pull_request.
# PullRequest triggers use the default GITHUB_TOKEN permissions.
# We need to add `pull-requests: write` because comments on a PR are technically under `pull-requests: write`.
old_perms = "permissions:\n  issues: write"
new_perms = "permissions:\n  issues: write\n  pull-requests: write"
content2 = content2.replace(old_perms, new_perms)

with open(file2, "w") as f:
    f.write(content2)
