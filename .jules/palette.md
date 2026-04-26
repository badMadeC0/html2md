## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-24 - [Fix color contrast on status messages]
**Learning:** The default "Red" foreground color often fails WCAG AA contrast ratio requirements for small text against default light gray or white application backgrounds. It's too bright/light.
**Action:** Use a darker, explicitly defined red, such as the Material Design red `#D32F2F`, for accessible error text states in standard UIs (including WPF apps). Ensure it provides at least a 4.5:1 contrast ratio.
