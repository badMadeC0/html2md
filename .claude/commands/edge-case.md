---
description: Append a new entry to pr-rules/edge-cases.md.
allowed-tools: Bash, Read, Edit
argument-hint: "<short description of the edge case>"
---

# /edge-case — Append to the edge-case ledger

Add a new row to `pr-rules/edge-cases.md` capturing an ambiguity that the
baseline rules did not cover, plus the decision taken.

## Steps

1. Read `pr-rules/edge-cases.md`. Find the highest existing `EC-NNNN` ID and
   pick the next one (`EC-0001` if the ledger is empty).
2. Determine today's date in ISO-8601 (`YYYY-MM-DD`).
3. Identify the affected file or area from the conversation context — the
   user's argument `$ARGUMENTS` is the short description.
4. Append a new row to the ledger table — never modify or delete existing
   rows. Columns:
   - ID (the new EC-NNNN)
   - Date (today)
   - File or area
   - Rule conflict / ambiguity (from `$ARGUMENTS`)
   - Decision (one sentence)
   - PR (current PR number from `gh pr view --json number -q .number`,
     or `pending` if no PR open yet)
5. Show the diff and confirm with the user before saving.

## Output

The new row, plus a one-line confirmation that the ledger was updated.
