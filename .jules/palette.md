# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2025-02-26 - PowerShell WPF Accessibility
**Learning:** Inline XAML in PowerShell scripts often lacks accessibility properties found in compiled apps because developers focus on visual layout. Explicit `AutomationProperties` (like `AutomationProperties.Name` and `AutomationProperties.HelpText`) are critical here since there's no code-behind or default accessors to set them dynamically for screen readers.
**Action:** Always audit PowerShell GUIs for `AutomationProperties` attributes on interactive elements, especially inputs and icon-only buttons.
