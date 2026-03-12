## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-30 - [Show tooltips on disabled buttons in WPF GUI]
**Learning:** In WPF applications (like `gui-url-convert.ps1`), elements that are disabled (`IsEnabled="False"`) do not display their `ToolTip` by default. This hides important context (e.g., *why* the button is disabled) from the user.
**Action:** Whenever using `IsEnabled="False"` on a button with an explanatory `ToolTip`, explicitly add `ToolTipService.ShowOnDisabled="True"` to ensure the tooltip is visible when hovering over the disabled control.
