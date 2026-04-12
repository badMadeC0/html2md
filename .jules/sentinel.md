## 2024-05-24 - Missing Security Headers in Flask App
**Vulnerability:** The Flask application (`src/html2md/app.py`) was serving API responses without common security headers (e.g., `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Content-Security-Policy`).
**Learning:** Default Flask apps do not automatically enforce these headers, requiring an `@app.after_request` handler.
**Prevention:** Always add a global response hook for security headers when bootstrapping new Flask or similar framework web applications to establish defense in depth against XSS, clickjacking, and MIME sniffing.
