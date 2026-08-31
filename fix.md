The CI check fails because:
"PR body contains AI-assistance transcript metadata, so the PR title must start with [AI-Assisted]."

Wait, my PR body had this URL:
`*PR created automatically by Jules for task [1986116096974025803](https://jules.google.com/task/1986116096974025803) started by @badMade*`

The PR check `ai-assisted-pr-guard.yml` enforces that if the PR body contains an agent transcript URL (like `https://jules.google.com/task/id`), the PR title MUST start with `[AI-Assisted]`.

But my PR title was:
`⚡ Bolt: Avoid string allocations in CSV sanitization hot path`

It should be:
`[AI-Assisted] ⚡ Bolt: Avoid string allocations in CSV sanitization hot path`
