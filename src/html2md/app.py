"""Flask application for html2md."""

import os

import time
from flask import Flask, jsonify, request

from html2md import __version__

DEFAULT_PORT = 10000

app = Flask(__name__)

# Simple in-memory rate limiter
RATE_LIMIT = 100  # requests
RATE_LIMIT_WINDOW = 60  # seconds
ip_requests = {}

@app.before_request
def rate_limit():
    """Rate limit requests based on IP address."""
    ip = request.remote_addr
    now = time.time()

    if ip not in ip_requests:
        ip_requests[ip] = []

    # Remove old requests outside the window
    ip_requests[ip] = [req_time for req_time in ip_requests[ip] if now - req_time < RATE_LIMIT_WINDOW]

    if len(ip_requests[ip]) >= RATE_LIMIT:
        return jsonify({'error': 'Too Many Requests'}), 429

    ip_requests[ip].append(now)

@app.teardown_request
def cleanup_rate_limit(exception=None):
    """Clean up empty IP entries to prevent memory leaks."""
    now = time.time()
    empty_ips = []
    for ip, req_times in ip_requests.items():
        ip_requests[ip] = [req_time for req_time in req_times if now - req_time < RATE_LIMIT_WINDOW]
        if not ip_requests[ip]:
            empty_ips.append(ip)

    for ip in empty_ips:
        del ip_requests[ip]


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@app.route('/health')
def health():
    """Return health status of the application."""
    return jsonify({'status': 'ok', 'service': 'html2md', 'version': __version__})


def get_host_port():
    """Get host and port from environment variables."""
    default_port = 10000
    port_str = os.environ.get('PORT')
    try:
        port_value = int(port_str) if port_str is not None else DEFAULT_PORT
    except ValueError:
        print(
            f'Warning: Invalid PORT environment variable value '
            f'{port_str!r}; falling back to default {default_port}.'
        )
        port_value = DEFAULT_PORT

    hostname = os.environ.get('HOST', '0.0.0.0')
    return hostname, port_value


if __name__ == '__main__':
    host, port = get_host_port()
    app.run(host=host, port=port)
