
## 2024-05-24 - Labels and Screen Reader Announcements in WPF GUI

**Learning:** For WPF applications using XAML to define UI (as in `gui-url-convert.ps1`), inputs should have `<Label>` associated with them, pointing to the input field using `Target="{Binding ElementName=...}"`. Status updates in elements like `TextBlock` do not inherently announce their text updates to screen readers unless configured with `AutomationProperties.LiveSetting="Polite"`.
**Action:** When working on WPF UI files, ensure `TextBox` fields have a designated `Label` with `Target` bound properly, and status text blocks should have `AutomationProperties.LiveSetting="Polite"` for screen readers to pick up state changes unobtrusively.

## 2024-05-25 - Use Grid instead of StackPanel for responsive horizontal layouts in WPF GUI

**Learning:** For horizontal layout components in WPF (`gui-url-convert.ps1`) like a text input field accompanied by buttons, `StackPanel` combined with fixed `Width` limits responsiveness when the window is resized. Using a `Grid` with `ColumnDefinitions` where the input field uses `Width="*"` and button columns use `Width="Auto"` allows the input to fluidly adapt to available space, significantly improving the UX for components displaying variable-length strings like file paths.
**Action:** Replace horizontal `StackPanel` layouts with `Grid` structures that use star/auto `ColumnDefinition` sizing (for example, `Width="*"` for the text input column and `Width="Auto"` for button columns), while keeping explicit fixed button widths only where they are intentionally needed.

## 2025-03-11 - Persistent Visual Context for Critical Inputs

**Learning:** While tooltips are helpful for supplementary information, critical inputs like directory paths require persistent visual context (labels). Solely relying on tooltips can leave sighted users disoriented when the tooltip is not active, leading to slower cognitive processing of the form's layout.
**Action:** Always provide persistent, visible labels (using `<Label>` controls with `Target` bindings for screen reader support) for core form elements, instead of relying exclusively on tooltips or placeholder text.
