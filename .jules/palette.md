# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-03-06 - Visual Labels vs AutomationProperties
**Learning:** While `AutomationProperties.Name` satisfies basic screen reader requirements for inputs, failing to provide an explicit, visible `<Label>` harms cognitive accessibility and removes standard keyboard mnemonic affordances (e.g. `Alt+Letter`) for sighted users.
**Action:** Always pair inputs with a visual, targeted `<Label>` element, and use keyboard mnemonics on the label to improve both screen reader and keyboard-only user experiences.