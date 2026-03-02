# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-18 - Avoid orphaned inputs by using visual labels
**Learning:** In desktop GUIs (like WPF), using `AutomationProperties.Name` and `ToolTip` on a `TextBox` provides basic accessibility, but omitting an explicitly linked visual `Label` (e.g., using `Target="{Binding ElementName=...}"`) forces visual users to guess the input's purpose based on context. Additionally, using rigid layout containers like `StackPanel` with hardcoded widths prevents the input from adapting to window resizes.
**Action:** Always pair important form inputs with a visual `Label` that provides an access key and is linked to the input. Use responsive layout containers like `Grid` with `*` width sizing instead of `StackPanel` to allow inputs to dynamically fill available space.
