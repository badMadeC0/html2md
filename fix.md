I tried submitting to the same branch `bolt-lstrip-optimization`, but it seems like `PR_TITLE` in the CI env isn't updating to `[AI-Assisted] ...`, or maybe the previous PR was just updated and the workflow was triggered on a push but still saw the original title. I will create a new PR on a new branch `bolt-lstrip-opt-v2` with the exact correct `[AI-Assisted]` prefix from the very beginning.

Wait! A closer look at the workflow rules:
It's triggered on `pull_request`.
The PR title *must* start with `[AI-Assisted]`.

Let's just submit on the new branch, making sure the title includes `[AI-Assisted]` right away.
