# Business rules

> Skeleton — populate with product-level invariants as they are agreed.

A "business rule" here is an invariant or constraint that the code must
preserve across changes. They may be enforced by tests, by hooks, or only
by review.

## Rule list

- **BR-0001 — `cli.py` is a placeholder.** No real conversion logic in
  this repo; the runtime ships separately. (Source: `pr-rules/service-html2md.md` §1.)
- **BR-0002 — log-export default fields.** `html2md-log-export` defaults to
  `ts,input,output,status,reason`. Changing this is a breaking change.
  (Source: `pr-rules/service-html2md.md` §2.)
- **BR-0003 — UTF-8 throughout.** All text I/O uses `encoding="utf-8"`.
  (Source: `pr-rules/python.md` §2.)
- **BR-0004 — Python 3.8 floor.** No syntax/APIs added after 3.8.
  (Source: `pr-rules/python.md` §1.)

<!--
  When adding a rule:
  - assign the next BR-NNNN ID
  - link to its source rule, ADR, or PR
  - keep the wording terse — one line if possible
-->
