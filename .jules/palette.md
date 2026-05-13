
## 2024-05-24 - Labels and Screen Reader Announcements in WPF GUI

**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-25 - [Use empty states and explanatory disabled states for WPF UIs]
**Learning:** For WPF applications using XAML, action buttons like "Clear" should have disabled states when there is nothing to act upon, and their `ToolTip` should explain why they are disabled (e.g., "URL list is already empty"). Similarly, output or log text boxes should provide an initial empty state text instead of being blank, so users know where output will appear (e.g., "Ready. Conversion logs will appear here...").
**Action:** When designing or updating WPF UI layouts, ensure buttons have logical `IsEnabled` rules and corresponding tooltips explaining the state, and use placeholder or empty state text in output text boxes.

## 2025-03-11 - Persistent Visual Context for Critical Inputs

**Learning:** While tooltips are helpful for supplementary information, critical inputs like directory paths require persistent visual context (labels). Solely relying on tooltips can leave sighted users disoriented when the tooltip is not active, leading to slower cognitive processing of the form's layout.
**Action:** Always provide persistent, visible labels (using `<Label>` controls with `Target` bindings for screen reader support) for core form elements, instead of relying exclusively on tooltips or placeholder text.
