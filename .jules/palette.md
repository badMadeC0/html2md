# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-06-25 - Responsive Layouts in WPF
**Learning:** Hardcoding left margins for layout in WPF (e.g. `Margin="150,15,0,0"`) creates fragile designs that easily break or overlap when users adjust system font sizes or DPI scaling. Proper `Grid` column definitions natively adapt to content width, making the UI much more accessible to users with visibility needs. Additionally, visual labels that use `Target` to link to inputs (`OutBox`) give blind users important context.
**Action:** Use `<Grid>` and `ColumnDefinitions` for row layouts rather than relying on `Margin` to position interactive elements relative to each other. Always add visual, explicit `Label`s with target bindings to interactive fields that lack them.
