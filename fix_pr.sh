git commit --amend -m "[AI-Assisted] 🛡️ Sentinel: [MEDIUM] Fix unintended network exposure in app

🚨 Severity: MEDIUM
💡 Vulnerability: The Flask application defaulted to binding to '0.0.0.0' when no HOST environment variable was provided, exposing it to all network interfaces.
🎯 Impact: Unintended network exposure of the application, potentially allowing unauthorized access if deployed in an environment where network access isn't restricted by a firewall.
🔧 Fix: Changed the default fallback host in src/html2md/app.py from '0.0.0.0' to '127.0.0.1' (localhost).
✅ Verification: Ran PYTHONPATH=src pytest to ensure no tests were broken. Review of the code confirms the fallback value in os.environ.get() is updated."
