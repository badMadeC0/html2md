# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-24 - Accessible Labels and Responsive Grids in WPF
**Learning:** In WPF interfaces like `gui-url-convert.ps1`, relying solely on `AutomationProperties.Name` or tooltips for text inputs isn't enough; visible labels bound with `Target="{Binding ElementName=...}"` are necessary for both screen readers and sighted users. Furthermore, hardcoded widths (like `Width="340"`) and margins (like `Margin="150,15,0,0"`) lead to brittle layouts that don't respond well to different screen sizes or resolutions.
**Action:** Always pair WPF text inputs with a visual `<Label>` utilizing the `Target` attribute. Use `<Grid>` definitions with `Width="*"` and `Width="Auto"` rather than `StackPanel` with hardcoded widths and margins to ensure responsive, accessible layouts.
