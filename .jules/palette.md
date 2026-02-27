# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-10-23 - Keyboard Shortcuts in Tooltips
**Learning:** Users often don't discover keyboard accelerators unless they are explicitly shown. Adding the shortcut key (e.g., "Alt+T") to the tooltip text makes these power-user features discoverable without cluttering the UI.
**Action:** Always append the keyboard shortcut to the tooltip text for any interactive element that has an accelerator key.

## 2024-10-23 - Live Regions for Status Updates
**Learning:** Screen reader users miss status updates (like "Processing..." or "Done") if they appear in static text elements without `LiveSetting`.
**Action:** Use `AutomationProperties.LiveSetting="Polite"` for status text blocks in XAML to ensure updates are announced.
