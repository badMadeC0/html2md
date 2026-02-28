# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-10-24 - explicit Label vs AutomationProperties in XAML
**Learning:** Relying solely on `AutomationProperties.Name` for text inputs hides the expected input's purpose from sighted users, and may be skipped by some screen readers in certain contexts if a visual label exists nearby but isn't properly linked.
**Action:** Always provide an explicit, visual `<Label>` linked to its text box via `Target="{Binding ElementName=...}"` for both accessibility and universal clarity.
