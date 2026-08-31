Wait, in my previous attempt to submit, I submitted with:
`[AI-Assisted] ⚡ Bolt: Avoid string allocations in CSV sanitization hot path`

However, the CI output still says:
`PR title: ⚡ Bolt: Avoid string allocations in CSV sanitization hot path`

This means my previous submit didn't actually use the `[AI-Assisted]` title in the pull request that the CI is testing. Wait, looking at the previous submit call, I used:
`title="[AI-Assisted] ⚡ Bolt: Avoid string allocations in CSV sanitization hot path"`

Ah! The second CI failure output is from a run that was executed at `2026-08-31T02:43:17` and the first at `2026-08-31T02:41:39`. Did I just need to wait, or did it fail again with the exact same PR title? Wait, the PR title in the second failure is still `⚡ Bolt: Avoid string allocations in CSV sanitization hot path`.
Let me verify my commit message and branch.

Wait, I think the `submit` tool might have failed to update the title of an existing PR, or maybe it created a new PR but the system somehow evaluated the old one, OR I just need to call `submit` again with the correct title.
Let's see my last submit payload.

Ah, the instructions state: "If you already submitted a change previously, you should continue using the same branch name."
I used `bolt-lstrip-optimization` both times.

Let's just submit again with the exact same title as required.
Wait, let me double check the `submit` tool implementation or just submit again.
