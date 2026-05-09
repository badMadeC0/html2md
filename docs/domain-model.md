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
- **Conversion runtime:** The HTML→Markdown / PDF / TXT conversion
  pipeline exposed by this project's CLI and documentation; this repo
  contains the interface/stub for that flow, while the full production
  runtime is delivered by a separate packaged build.
