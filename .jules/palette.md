# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-10-24 - Dynamic Action Affordances in Text Input
**Learning:** In desktop GUI tools (like PowerShell WPF), maintaining static `IsEnabled` states for action buttons (e.g., "Convert" or "Clear") when the primary text input is empty causes confusion because the affordance suggests an action is possible when it isn't. Users expect immediate visual feedback linking the presence of input to the availability of subsequent actions.
**Action:** Always bind the `IsEnabled` state of primary action and clear buttons to the content length or presence of the primary text input using `TextChanged` events. Initialize this state explicitly on load.
