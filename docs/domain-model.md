# Domain model

> Skeleton — populate as the domain stabilizes.

The vocabulary the project uses internally and externally.

## Entities

<!--
  When adding an entity, document:
  - what it represents
  - its identifier (if any)
  - which module owns it
  - which other entities it relates to
-->

| Entity | Owner module | Identifier | Relates to |
| ------ | ------------ | ---------- | ---------- |
|        |              |            |            |

## Glossary

- **JSONL log:** Newline-delimited JSON file produced by the runtime,
  consumed by `html2md-log-export`. Default fields: `ts`, `input`,
  `output`, `status`, `reason`.
- **Conversion runtime:** The production HTML→Markdown / PDF / TXT
  conversion implementation used by this repository. The current
  in-repo runtime entry point is `src/html2md/cli.py`, which owns URL
  fetching and conversion behavior for contributor and packaging
  workflows.
