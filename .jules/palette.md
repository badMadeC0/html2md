# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2026-03-06 - Improve WPF GUI Accessibility
**Learning:** PowerShell WPF GUIs often lack native accessibility features like linked labels and default button behaviors out-of-the-box when built from raw XAML strings. Adding `Target="{Binding ElementName=...}"` to Labels and `IsDefault="True"` to the primary action Button drastically improves keyboard navigation and screen reader support with minimal code.
**Action:** Always check custom XAML/WPF forms for proper Label-to-Input bindings and ensure a default action button is defined for keyboard users.
