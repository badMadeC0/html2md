# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2026-03-03 - WPF Accessibility and Responsive Layouts
**Learning:** Using `AutomationProperties.LiveSetting="Polite"` on status text blocks is critical for screen readers to announce background progress without stealing focus. Also, hardcoding `Margin` on inline options (like checkboxes) causes severe overlap on high-DPI scaling.
**Action:** Use `WrapPanel` instead of hardcoded absolute margins to ensure form elements respond smoothly to window and text scaling in WPF GUIs. Always consider `LiveSetting` for dynamic feedback text.
