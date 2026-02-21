"""Flask application for html2md."""

import os

from flask import Flask, jsonify

from html2md import __version__

app = Flask(__name__)


@app.route('/health')
def health():
    """Return health status of the application."""
    return jsonify({'status': 'ok', 'service': 'html2md', 'version': __version__})


def get_host_port():
    """Get host and port from environment variables."""
    port_str = os.environ.get('PORT')
    try:
        port_value = int(port_str) if port_str is not None else default_port
    except ValueError:
        app.logger.warning(
            f'Warning: Invalid PORT environment variable value '
            f'{port_str!r}; falling back to default {DEFAULT_PORT}.'
        )
        port_value = default_port

    hostname = os.environ.get('HOST', '127.0.0.1')
    return hostname, port_value


if __name__ == '__main__':
    host, port = get_host_port()
    app.run(host=host, port=port)
