# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-22 - Desktop GUI Mnemonics and Shortcuts
**Learning:** In desktop GUIs (like WPF), keyboard users rely heavily on mnemonics (Alt+Key) and tab order. Adding explicit "Paste" and "Clear" buttons significantly improves usability for mouse users, while careful mnemonic selection (e.g., `Clea_r` to avoid conflict with `_Convert`) ensures keyboard efficiency isn't compromised.
**Action:** Always map shortcuts for primary actions and check for conflicts in the visual label.

## 2024-10-18 - WPF Default Text Contrast
**Learning:** The default `Gray` color in WPF (and many UI frameworks) often fails WCAG AA contrast guidelines on light backgrounds (approx 3.95:1). For status text or hints, use a darker shade like `#555555` (DimGray) to ensure readability for all users while maintaining visual hierarchy.
**Action:** Always verify color contrast ratios for "subtle" text colors using a contrast checker.
