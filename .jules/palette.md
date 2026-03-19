## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-25 - [Enable tooltips on disabled elements in WPF]
**Learning:** WPF disables ToolTips on disabled controls by default. This is an anti-pattern for UX/accessibility because it hides helpful guidance (like why a button is disabled) from the user exactly when they need it most.
**Action:** When disabling buttons (e.g. `IsEnabled="False"`), always add `ToolTipService.ShowOnDisabled="True"` to ensure the explanation tooltip remains visible to users.
