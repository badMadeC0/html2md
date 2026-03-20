## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-06-19 - [Add explicit AutomationProperties to all inputs and buttons in WPF GUI]
**Learning:** While tooltips provide visual context for hover, screen readers often need explicit `AutomationProperties.Name` and `AutomationProperties.HelpText` directly on WPF interactive controls (like `Button`, `TextBox`, and `CheckBox`) to ensure full keyboard navigation support and auditory context when focus changes.
**Action:** Always complement `ToolTip` attributes in XAML with `AutomationProperties.Name` and `AutomationProperties.HelpText` to ensure parity between visual helpers and screen reader announcements.
