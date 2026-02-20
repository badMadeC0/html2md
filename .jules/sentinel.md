## 2024-03-24 - PowerShell Command Injection Risk

**Vulnerability:** Unsanitized user inputs in `gui-url-convert.ps1` were passed directly to `cmd.exe /c` within a string argument, allowing for command injection via double quotes or special characters.
**Learning:** PowerShell's string interpolation and argument passing to external processes (especially `cmd.exe`) must be carefully handled. Simply wrapping variables in quotes is insufficient if the variables themselves can contain quotes.
**Prevention:**
1. Validate inputs against strict patterns (e.g., `[System.Uri]` for URLs).
2. Reject inputs containing dangerous characters (like double quotes) when constructing command strings manually.
3. When possible, use `Start-Process -ArgumentList` with an array of arguments, which handles escaping more safely than building a single command string. If string concatenation must be used, validate/reject CMD metacharacters (e.g., ``&|<>^()``) in user-supplied input.
