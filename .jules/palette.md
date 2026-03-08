# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2026-03-08 - Missing Visible Label for Output Directory Input
**Learning:** Found an input field (`OutBox`) that had `AutomationProperties.Name` and a `ToolTip` but no visible `<Label>`. While this was technically accessible to screen readers, sighted users lacked visual context for what the input was for. `Target="{Binding ElementName=...}"` provides both visual context and an expanded clickable area (especially when combined with mnemonics like `_T` in `Save _To:`).
**Action:** Always ensure important input fields have visible, associated `<Label>` controls, not just automation properties, to improve usability for all users and provide keyboard mnemonics (Alt+T).
