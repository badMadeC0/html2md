# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-24 - Accessible Forms in WPF
**Learning:** Fixed-width layouts with missing `Label` targets hinder accessibility and responsive window resizing in WPF interfaces. Inputs like "Output Directory" often lack screen reader context if not paired with a `<Label Target="...">`.
**Action:** Use responsive `<Grid>` layouts with proportional sizing (`*`) for primary inputs and always pair input fields with `<Label>` elements using explicit `Target="{Binding ElementName=...}"` and accelerator keys (e.g., `_Paste`, `O_utput`) for keyboard navigation.
