# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-18 - Missing Visible Labels and Rigid Layouts in WPF TextBoxes
**Learning:** Found a pattern where input fields (like the Output Directory TextBox) relied solely on `AutomationProperties.Name` and tooltip for accessibility, missing a visible `Label`. Additionally, the layout used a rigid `StackPanel` with fixed-width `TextBox`, making it inflexible.
**Action:** Replaced `StackPanel` with a `Grid` layout, adding an explicit visible `Label` using `Target="{Binding ElementName=[TargetName]}"` for proper screen reader association and keyboard navigation (Alt+key). Changed `TextBox` width to `*` in the `Grid` column definitions to allow it to dynamically resize and fill available space.
