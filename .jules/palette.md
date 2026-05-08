
## 2024-05-24 - Labels and Screen Reader Announcements in WPF GUI

**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-25 - [Context-aware disabled state and focus management for clear buttons in GUI]
**Learning:** For a more accessible and intuitive UI, buttons that perform an action on an input field (like a 'Clear' button) should be context-aware and dynamically disable when the input is empty. Crucially, when an action clears an input and thus triggers the button's disabled state, keyboard focus must be manually returned to the input *before* the clearing action occurs; otherwise, focus is lost when the active element becomes disabled, creating a confusing experience for keyboard and screen reader users.
**Action:** When creating or modifying dynamic buttons that alter input state, ensure their `IsEnabled` status is bound to the input's content changes, and actively manage focus back to a stable element prior to executing a disabling action.

## 2025-03-11 - Persistent Visual Context for Critical Inputs

**Learning:** While tooltips are helpful for supplementary information, critical inputs like directory paths require persistent visual context (labels). Solely relying on tooltips can leave sighted users disoriented when the tooltip is not active, leading to slower cognitive processing of the form's layout.
**Action:** Always provide persistent, visible labels (using `<Label>` controls with `Target` bindings for screen reader support) for core form elements, instead of relying exclusively on tooltips or placeholder text.
