# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-24 - Avoid Hardcoded Layout Margins in WPF
**Learning:** Hardcoded horizontal margins (e.g., `Margin="150,15,0,0"`) to position controls inline in XAML make the layout extremely fragile, particularly failing when users have higher DPI screens, larger system font sizes, or when the application is translated to different languages with varying text widths.
**Action:** Always use layout containers like `StackPanel` or `Grid` for grouping controls side-by-side, relying on natural flow and small relative margins (e.g., right margin of 15) rather than absolute positioning or large offset margins from the parent.
