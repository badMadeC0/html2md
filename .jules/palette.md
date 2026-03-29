## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-25 - [Show tooltips on disabled elements in WPF GUI]
**Learning:** In WPF (Windows Presentation Foundation) XAML definitions, tooltips on elements do not display by default when the element is disabled (`IsEnabled="False"`). If a disabled control has a helpful tooltip explaining *why* it's disabled, users will never see it unless explicitly configured.
**Action:** When creating WPF controls that convey disabled state reasons via `ToolTip`, add the attached property `ToolTipService.ShowOnDisabled="True"` to ensure the accessibility/UX information is actually presented to the user.
