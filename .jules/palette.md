
## 2024-05-24 - Labels and Screen Reader Announcements in WPF GUI

**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2026-04-14 - [Ensure tooltips are visible on disabled buttons in WPF]
**Learning:** In WPF applications (like `gui-url-convert.ps1`), tooltips on UI elements are hidden by default when the element is in a disabled state (`IsEnabled="False"`). This means helpful explanations of *why* an action is disabled (e.g., "Please enter at least one URL to enable conversion") are invisible to the user until the control is enabled.
**Action:** When creating WPF interfaces with disabled buttons that require explanation, explicitly set `ToolTipService.ShowOnDisabled="True"` on the element to ensure the tooltip remains visible and helpful regardless of the button's enabled state.

## 2025-03-11 - Persistent Visual Context for Critical Inputs

**Learning:** While tooltips are helpful for supplementary information, critical inputs like directory paths require persistent visual context (labels). Solely relying on tooltips can leave sighted users disoriented when the tooltip is not active, leading to slower cognitive processing of the form's layout.
**Action:** Always provide persistent, visible labels (using `<Label>` controls with `Target` bindings for screen reader support) for core form elements, instead of relying exclusively on tooltips or placeholder text.
