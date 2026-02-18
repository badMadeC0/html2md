## 2024-05-22 - Non-blocking Feedback in PowerShell GUIs
**Learning:** PowerShell WPF scripts often rely on `MessageBox` for feedback, which halts user interaction. Replacing these with a `StatusBar` or dedicated feedback area provides a smoother, more modern experience without requiring complex code changes.
**Action:** Identify `MessageBox` calls in scripts and replace them with non-blocking status updates where appropriate.

## 2024-05-22 - Initial Focus Accessibility
**Learning:** Many simple GUI scripts forget to set initial focus, forcing users to click before typing. Using `FocusManager.FocusedElement` in XAML is a robust, declarative fix.
**Action:** Verify initial focus state in all GUI windows and add explicit focus management.
