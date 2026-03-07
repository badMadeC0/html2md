# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2025-02-28 - WPF Accessibility & Responsive Layouts
**Learning:** Hardcoded widths (like `Width="340"`) and implicit context in a `StackPanel` create fragile UI and poor screen reader experiences. In WPF, inputs benefit immensely from an explicitly associated visual `Label` (using `Target="{Binding ElementName=...}"`) which provides both context and a keyboard shortcut.
**Action:** Use a `Grid` with `ColumnDefinition Width="*"` for fluid text inputs, and always pair inputs with a `Label` control for a11y and keyboard navigability rather than relying solely on `AutomationProperties.Name`.
