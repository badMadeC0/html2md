# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-28 - Explicit Automation Names for Primary Inputs
**Learning:** While some fields have accompanying labels, it is best practice for key UI components (like the primary URL input text box) to have an explicitly defined `AutomationProperties.Name` so that screen readers correctly and directly announce the purpose of the input when it receives focus, especially if focus management places the cursor there automatically.
**Action:** Always ensure critical or initially focused input fields use `AutomationProperties.Name` for maximum accessibility.
