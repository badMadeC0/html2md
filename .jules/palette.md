## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-25 - [Add ToolTipService.ShowOnDisabled to disabled buttons]
**Learning:** In WPF XAML, tooltips on elements that have `IsEnabled="False"` do not show up by default when the user hovers over them. This hides helpful explanations (like why the button is disabled) from the user.
**Action:** When working on WPF UI files, ensure disabled elements that need to explain their state have `ToolTipService.ShowOnDisabled="True"` added to them so the user is not left confused.
