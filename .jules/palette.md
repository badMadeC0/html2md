# Palette's Journal - Critical Learnings

## 2024-05-24 - Missing explicit labels on file path inputs
**Learning:** In WPF applications within this repository, file path inputs (like the Output Directory) often rely solely on adjacent buttons ("Browse") or `AutomationProperties.Name` for context, missing explicit visual labels. This harms both visual UX (scanning) and explicit screen reader targeting via `Target` binding.
**Action:** Always ensure horizontal form fields, especially file paths, include a preceding `<Label Target="{Binding ElementName=...}">` to provide explicit visual and accessibility context.
