## 2023-10-27 - Added Missing Security Headers to Flask App
**Vulnerability:** The Flask application `src/html2md/app.py` did not include appropriate security headers like `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, or `Strict-Transport-Security`.
**Learning:** This missing configuration could make the application vulnerable to basic web attacks like clickjacking, MIME-type sniffing, or missing enforcing HTTPS.
**Prevention:** Ensure standard security headers are applied to the Flask app. Added `@app.after_request` handler to set the headers on all responses. Always verify security header implementation when developing new web endpoints.
