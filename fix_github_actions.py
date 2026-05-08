import re

# Fix 1: remove or comment out google-gemini/code-assist-action
file1 = ".github/workflows/gemini-code-assist.yml"
with open(file1, "r") as f:
    content1 = f.read()
# Comment it out because the repo doesn't exist anymore
content1 = re.sub(
    r"(?m)^(\s*)uses: google-gemini/code-assist-action@v1",
    r"\1# uses: google-gemini/code-assist-action@v1",
    content1,
)
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
permissions_match = re.search(r"(?m)^permissions:\n(?P<body>(?:^  [^\n]+\n?)+)", content2)
if permissions_match:
    permissions_body = permissions_match.group("body")
    if "pull-requests:" not in permissions_body:
        updated_body = re.sub(
            r"(?m)^(  issues: write\n?)",
            r"\1  pull-requests: write\n",
            permissions_body,
            count=1,
        )
        if updated_body == permissions_body:
            updated_body = f"{permissions_body.rstrip()}\n  pull-requests: write\n"
        content2 = (
            content2[: permissions_match.start("body")]
            + updated_body
            + content2[permissions_match.end("body") :]
        )
else:
    content2 += "\npermissions:\n  issues: write\n  pull-requests: write\n"

with open(file2, "w") as f:
    f.write(content2)
