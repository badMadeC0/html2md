## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-25 - [Use non-blocking StatusText over MessageBox for form validation in WPF]
**Learning:** Using `[System.Windows.MessageBox]::Show` blocks the main UI thread in WPF/PowerShell applications and forces the user to manually dismiss a dialog for minor validation errors, which disrupts the flow.
**Action:** Replace blocking MessageBox dialogs with inline feedback updates, such as setting `$StatusText.Text` with error messages, changing the text color to "Red" for visibility, and ensuring `$ProgressBar.IsIndeterminate = $false` is set to revert loading states.
