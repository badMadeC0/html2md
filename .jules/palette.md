# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2024-05-15 - [Accessible Layouts in WPF]
**Learning:** In WPF (Windows Presentation Foundation) desktop UIs, `StackPanel` layouts can sometimes inadvertently encourage omitting properly associated labels. Using a `Grid` layout not only makes alignment cleaner but makes it easier to position a visible `Label` properly next to an input control. Providing a visible `Label` with an access key (e.g., `_Output:`) and a `Target="{Binding ElementName=ControlName}"` is superior to relying solely on `AutomationProperties.Name` because it provides both screen reader accessibility and keyboard shortcut support (Alt+key focus) simultaneously, aiding users with mobility impairments.
**Action:** Whenever introducing inputs in WPF/XAML, prefer a `Grid` layout to pair the input with a visible, target-bound `Label` containing an access key, falling back to `AutomationProperties.Name` only for explicitly label-less controls (like the URL box in this case which had a label in another Grid row).
