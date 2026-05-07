"""Flask application for html2md."""

import os

from flask import Flask, jsonify

from html2md import __version__

DEFAULT_PORT = 10000
LOCAL_HOST = '127.0.0.1'
DEPLOY_HOST = '0.0.0.0'

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

    # Keep direct local runs private by default, but preserve the common
    # container/PaaS convention where the platform provides PORT and expects
    # the process to listen on all interfaces unless HOST is explicitly set.
    default_host = DEPLOY_HOST if port_str is not None else LOCAL_HOST
    hostname = os.environ.get('HOST', default_host)
    return hostname, port_value


if __name__ == '__main__':
    host, port = get_host_port()
    app.run(host=host, port=port)
