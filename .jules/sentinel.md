## 2024-05-22 - Untrusted Input in Logs
**Vulnerability:** CSV Injection in log export
**Learning:** The application logs user-supplied URLs directly. When these logs are exported to CSV, malicious payloads (e.g., `=cmd|...`) can be executed by spreadsheet software.
**Prevention:** Sanitize all fields starting with `=`, `+`, `-`, `@` by prepending `'` in any CSV export functionality.
