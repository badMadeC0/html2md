# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-10-18 - PowerShell XAML Accessibility
**Learning:** PowerShell WPF GUIs defined via inline XAML often miss standard accessibility features like Labels with Target bindings, relying solely on AutomationProperties.
**Action:** When reviewing PowerShell GUIs, explicitly check for visual labels and ensure `Target="{Binding ElementName=...}"` is used to associate them with inputs for screen readers and keyboard navigation.
