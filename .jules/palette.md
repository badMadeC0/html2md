# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2026-03-08 - WPF Status Bar Accessibility & Contrast Defaults
**Learning:** Default WPF colors like `Gray` and `Red` on light backgrounds frequently fail WCAG AA contrast ratio requirements. Additionally, `StatusBar` updates are not naturally announced by screen readers without specific accessibility attributes.
**Action:** When updating a WPF or PowerShell XAML UI, use `#555555` for gray text and `#CC0000` for red text. Ensure that live status indicators use `AutomationProperties.LiveSetting="Assertive"` (or "Polite") so screen readers can audibly announce changes as they happen.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2026-03-08 - Missing Visible Label for Output Directory Input
**Learning:** Found an input field (`OutBox`) that had `AutomationProperties.Name` and a `ToolTip` but no visible `<Label>`. While this was technically accessible to screen readers, sighted users lacked visual context for what the input was for. `Target="{Binding ElementName=...}"` provides both visual context and an expanded clickable area (especially when combined with mnemonics like `_T` in `Save _To:`).
**Action:** Always ensure important input fields have visible, associated `<Label>` controls, not just automation properties, to improve usability for all users and provide keyboard mnemonics (Alt+T).

## 2026-03-08 - Keyboard Accelerators & Dynamic Button State
**Learning:** In WPF/PowerShell XAML, multiple controls can accidentally share the same keyboard accelerator (e.g., Alt+T for "Paste" and "Save To" using `_`). Additionally, primary action buttons should ideally communicate *why* they are disabled when required input is missing.
**Action:** Always verify that keyboard mnemonics (using `_` in Content/Label) are unique across the UI. Use dynamic `ToolTip` and `IsEnabled` properties on primary buttons, tied to `TextChanged` events of required inputs, to guide users rather than letting them click and fail.
