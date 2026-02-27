# Sentinel Journal

This journal records CRITICAL security learnings, vulnerabilities, and patterns found in the codebase.

## 2024-10-24 - CSV Injection in Log Export
**Vulnerability:** The `log_export.py` script directly wrote user-controlled input (JSON logs) to CSV without sanitization. If a log entry contained fields starting with `=`, `+`, `-`, or `@`, opening the CSV in Excel could execute arbitrary code (CSV Injection).
**Learning:** `csv.DictWriter` does not automatically sanitize fields for formula injection. Any tool exporting user data to CSV must explicitly sanitize formula triggers.
**Prevention:** Prefix any field value starting with `=`, `+`, `-`, or `@` with a single quote `'` to force it to be treated as text by spreadsheet applications.

## 2024-10-24 - Command Injection in PowerShell GUI
**Vulnerability:** `gui-url-convert.ps1` constructs a command string using unescaped user input (`$url` and `$outdir`) inside a single-quoted string context passed to `powershell -Command`. A malicious URL containing a single quote `'` allows arbitrary PowerShell code execution.
**Learning:** String concatenation for command construction is dangerous, even in PowerShell. Using `Start-Process -ArgumentList` with an array of arguments is safer than building a command string.
**Prevention:** Avoid `Invoke-Expression` or `powershell -Command "..."`. Use `& $exe $args` where `$args` is an array, or `Start-Process` with `ArgumentList`.

## 2024-03-01 - XSS in Markdown Conversion
**Vulnerability:** The `html2md` CLI blindly converted HTML to Markdown without sanitization. Malicious attributes like `<a href="javascript:alert(1)">` were preserved in the Markdown output as `[link](javascript:alert(1))`, leading to Cross-Site Scripting (XSS) when rendered by Markdown viewers.
**Learning:** Markdown conversion libraries (like `markdownify`) often prioritize fidelity over security and do not sanitize dangerous schemes by default.
**Prevention:** Always sanitize HTML input using a dedicated library (like `BeautifulSoup`) to remove scripts, event handlers, and dangerous URI schemes (`javascript:`, `vbscript:`, `data:`) *before* passing it to any conversion tool.
