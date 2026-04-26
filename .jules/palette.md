# 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]

**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2025-04-05 - [Disable action buttons dynamically based on input state]
**Learning:** In WPF applications, buttons performing actions like "Clear" on an input field should be dynamically disabled when the input is empty to prevent user confusion and provide immediate visual feedback.
**Action:** Always link the `IsEnabled` state of such buttons to the `TextChanged` event of the corresponding input field, and initialize them properly in XAML.
