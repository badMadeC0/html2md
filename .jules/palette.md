## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-24 - [Replace blocking MessageBox validation with inline status updates]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), blocking `MessageBox` errors disrupt user flow. Non-blocking inline `StatusBar` text updates are better for form validation errors, taking advantage of polite screen reader announcements via `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, avoid `MessageBox` popups for validation and use `$StatusText.Text` and `$StatusText.Foreground = "Red"` to show inline error messages.
