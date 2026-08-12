## 2024-05-08 - Added Request Size Limits to Prevent Denial of Service
**Vulnerability:** The CLI fetched remote URLs directly into memory without any size constraints. A malicious or misconfigured server returning a multi-gigabyte HTML response would cause an Out of Memory (OOM) error, creating a Denial of Service (DoS) vulnerability.
**Learning:** Even simple CLI fetch tools are susceptible to resource exhaustion attacks if response sizes are unbounded, especially since `requests.get` without `stream=True` buffers the entire response in memory.
**Prevention:** Always use `stream=True` when downloading untrusted resources, and enforce a strict upper limit on downloaded bytes.
## 2024-08-12 - AI-Assisted PR Metadata Requirements
**Learning:** PR titles must start with `[AI-Assisted]` when the body contains an AI transcript URL (e.g. `jules.google.com/task/...`) to pass the GitHub Actions CI check "Verify AI-assisted PR metadata".
**Action:** Always include the `[AI-Assisted]` prefix in the PR title for tasks involving AI agents in this project to prevent CI failures.
