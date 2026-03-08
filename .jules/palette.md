# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2026-03-08 - WPF Status Bar Accessibility & Contrast Defaults
**Learning:** Default WPF colors like `Gray` and `Red` on light backgrounds frequently fail WCAG AA contrast ratio requirements. Additionally, `StatusBar` updates are not naturally announced by screen readers without specific accessibility attributes.
**Action:** When updating a WPF or PowerShell XAML UI, use `#555555` for gray text and `#CC0000` for red text. Ensure that live status indicators use `AutomationProperties.LiveSetting="Assertive"` (or "Polite") so screen readers can audibly announce changes as they happen.
