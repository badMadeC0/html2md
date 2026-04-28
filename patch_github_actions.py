import os
import re

file_path = ".github/workflows/gemini-code-assist.yml"
with open(file_path, "r") as f:
    content = f.read()

# Replace with the new repo, it appears "google-gemini/code-assist-action" was moved or removed.
# I'll just remove the job completely or comment it out if it's the only job.
