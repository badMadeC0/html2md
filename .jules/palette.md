## 2026-03-19 - [Add keyboard shortcut hints to GUI tooltips]
**Learning:** While access keys (using `_` in WPF Content attributes, triggering `Alt+Key` shortcuts) provide keyboard navigation, their discoverability is poor. Users typically have to probe by holding `Alt` to see them. Adding explicit shortcut hints to tooltips (e.g., `(Alt+C)`) makes these time-saving shortcuts discoverable and significantly improves power-user UX.
**Action:** Always append the corresponding keyboard shortcut hint (e.g., `(Alt+C)`) to the ToolTip text of UI elements that have access keys defined.

## 2024-05-24 - [Add labels to output directory field and screen reader polite announcement for status bar in GUI]
**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.
