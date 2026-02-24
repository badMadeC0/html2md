# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-22 - Desktop GUI Mnemonics and Shortcuts
**Learning:** In desktop GUIs (like WPF), keyboard users rely heavily on mnemonics (Alt+Key) and tab order. Adding explicit "Paste" and "Clear" buttons significantly improves usability for mouse users, while careful mnemonic selection (e.g., `Clea_r` to avoid conflict with `_Convert`) ensures keyboard efficiency isn't compromised.
**Action:** Always map shortcuts for primary actions and check for conflicts in the visual label.

## 2026-02-24 - Implicit Directory Inputs vs. Explicit Labels
**Learning:** Complex form inputs like directory paths are often implicitly labeled by their adjacent "Browse" buttons in developer-centric tools, but this fails WCAG 2.1 Success Criterion 2.5.3 (Label in Name) for sighted users who rely on visual labels.
**Action:** Always wrap directory inputs in a vertical stack with an explicit `Label` control bound via `Target` property, even if space is tight.
