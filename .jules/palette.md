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

## 2026-03-09 - Disabling action buttons when required input is missing
**Learning:** Found that "Convert" and "Clear" buttons in the URL converter UI were left enabled even when the URL input was completely empty. This can mislead users into trying invalid actions. Disabling action buttons dynamically based on input state makes the interface more intuitive and prevents user error.
**Action:** When a button requires text input to function correctly, always bind an event listener to the text box (e.g., `Add_TextChanged`) and update the button's `IsEnabled` property based on whether valid text is present. Set `IsEnabled="False"` by default in the XAML for these buttons.
