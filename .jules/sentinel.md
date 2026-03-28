# Sentinel Security Journal

## 2024-03-28 - Missing Security Headers in Flask App
**Vulnerability:** The Flask application `app.py` does not set security headers (CSP, X-Frame-Options, etc.), increasing the risk of XSS and clickjacking if the app expands beyond API endpoints.
**Learning:** Even simple API or utility applications should enforce security headers to establish defense-in-depth and establish secure baselines.
**Prevention:** Integrate a security header middleware (e.g., `@app.after_request` or Flask-Talisman) by default for all new web interfaces.
