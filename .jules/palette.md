## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-10-25 - [Ensure Accessible Error Colors in WPF]
**Learning:** Using the default "Red" (`#FF0000`) for error text in WPF status bars/labels fails WCAG AA contrast ratio requirements (4.5:1) against standard gray/white backgrounds (actual contrast is ~3.5:1 to 3.9:1).
**Action:** Use a darker red like `#D32F2F` or `DarkRed` (`#8B0000`) for error states to maintain accessibility and readability while providing clear visual feedback.
