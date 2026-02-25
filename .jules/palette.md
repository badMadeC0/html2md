# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-22 - Desktop GUI Mnemonics and Shortcuts
**Learning:** In desktop GUIs (like WPF), keyboard users rely heavily on mnemonics (Alt+Key) and tab order. Adding explicit "Paste" and "Clear" buttons significantly improves usability for mouse users, while careful mnemonic selection (e.g., `Clea_r` to avoid conflict with `_Convert`) ensures keyboard efficiency isn't compromised.
**Action:** Always map shortcuts for primary actions and check for conflicts in the visual label.

## 2024-05-23 - Status Feedback vs. Modal Dialogs
**Learning:** Replacing modal error dialogs with status bar messages in desktop GUIs keeps users in the flow and reduces friction, especially for common validation errors. However, it's critical to ensure any "busy" indicators (like ProgressBars) are explicitly stopped when validation fails, otherwise the interface appears stuck.
**Action:** Use non-blocking status updates for validation feedback and audit all early-return paths to ensure UI state is reset.
