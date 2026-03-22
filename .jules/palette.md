## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-25 - [Enable Tooltips on Disabled WPF Buttons]
**Learning:** In WPF applications using XAML, tooltips on disabled elements (like buttons) do not display by default. This creates an accessibility and UX issue because users cannot see the explanation of why the control is disabled (e.g. "Please enter at least one URL to enable conversion").
**Action:** When working on WPF UI files, ensure disabled buttons that provide helpful context have `ToolTipService.ShowOnDisabled="True"` explicitly set so that screen readers and hover interactions can surface the tooltip text.
