## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-24 - [Add empty states and improve error contrast in WPF]
**Learning:** Empty `TextBox` outputs can feel broken or unready to users. Providing an initial placeholder (e.g., via the `Text` property) establishes clear expectations. Furthermore, error states must use accessible colors (like `#CC0000` instead of `Red`) to ensure a contrast ratio of at least 4.5:1 against typical backgrounds.
**Action:** When creating text output fields or logging views, initialize them with a helpful empty state message, and verify all feedback colors meet WCAG AA contrast standards.
