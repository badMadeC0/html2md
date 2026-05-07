## 2026-05-07 - [Sentinel] Fixed CWE-605 Default Binding Issue
**Vulnerability:** The Flask application in `src/html2md/app.py` defaulted to binding to all interfaces (`0.0.0.0`).
**Learning:** This could unintentionally expose the application to the network without adequate security measures (e.g., lack of authentication/authorization). Applications should default to localhost and only bind to external interfaces when explicitly requested.
**Prevention:** Avoid using `'0.0.0.0'` as a default fallback for `HOST` environment variables. Default to `'127.0.0.1'` (localhost) to ensure the principle of least privilege is applied unless configured otherwise.
