## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-25 - [Make ToolTips visible on disabled WPF controls]
**Learning:** In WPF (used in `gui-url-convert.ps1`), `ToolTip`s on elements like `<Button>` are hidden by default when the element is disabled (`IsEnabled="False"`). If the tooltip contains crucial information explaining *why* the element is disabled, this creates an accessibility and usability issue because users cannot see the explanation.
**Action:** When adding a helpful explanation to a disabled control via a `ToolTip`, always add the `ToolTipService.ShowOnDisabled="True"` attached property to ensure it remains visible and accessible to users when disabled.
