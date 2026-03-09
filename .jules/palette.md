# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-22 - Desktop GUI Mnemonics and Shortcuts
**Learning:** In desktop GUIs (like WPF), keyboard users rely heavily on mnemonics (Alt+Key) and tab order. Adding explicit "Paste" and "Clear" buttons significantly improves usability for mouse users, while careful mnemonic selection (e.g., `Clea_r` to avoid conflict with `_Convert`) ensures keyboard efficiency isn't compromised.
**Action:** Always map shortcuts for primary actions and check for conflicts in the visual label.

## 2024-10-18 - WPF Default Text Contrast
**Learning:** The default `Gray` color in WPF (and many UI frameworks) often fails WCAG AA contrast guidelines on light backgrounds (approx 3.95:1). For status text or hints, use a darker shade like `#555555` to ensure readability for all users while maintaining visual hierarchy.
**Action:** Always verify color contrast ratios for "subtle" text colors using a contrast checker.
## 2026-03-08 - WPF Status Bar Accessibility & Contrast Defaults
**Learning:** Default WPF colors like `Gray` and `Red` on light backgrounds frequently fail WCAG AA contrast ratio requirements. Additionally, `StatusBar` updates are not naturally announced by screen readers without specific accessibility attributes.
**Action:** When updating a WPF or PowerShell XAML UI, use `#555555` for gray text and `#CC0000` for red text. Ensure that live status indicators use `AutomationProperties.LiveSetting="Assertive"` (or "Polite") so screen readers can audibly announce changes as they happen.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2026-03-08 - Missing Visible Label for Output Directory Input
**Learning:** Found an input field (`OutBox`) that had `AutomationProperties.Name` and a `ToolTip` but no visible `<Label>`. While this was technically accessible to screen readers, sighted users lacked visual context for what the input was for. `Target="{Binding ElementName=...}"` provides both visual context and an expanded clickable area (especially when combined with mnemonics like `_T` in `Save _To:`).
**Action:** Always ensure important input fields have visible, associated `<Label>` controls, not just automation properties, to improve usability for all users and provide keyboard mnemonics (Alt+T).
