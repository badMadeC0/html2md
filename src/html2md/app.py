"""Flask application for html2md."""

import os

from flask import Flask, jsonify

from html2md import __version__

DEFAULT_PORT = 10000

app = Flask(__name__)


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


    # SECURITY: Default to 127.0.0.1 (localhost) instead of 0.0.0.0 (all interfaces).
    # Running the Flask development server on 0.0.0.0 exposes it to the network,
    # which is insecure. In production, use a production WSGI server like Gunicorn:
    # gunicorn -b 0.0.0.0:10000 html2md.app:app
    hostname = os.environ.get('HOST', '127.0.0.1')
    return hostname, port_value


if __name__ == '__main__':
    host, port = get_host_port()
    app.run(host=host, port=port)
