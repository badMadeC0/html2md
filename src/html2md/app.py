"""Flask application for html2md."""

import os

try:
    from flask import Flask, jsonify
except ImportError:
    # Flask is an optional dependency
    Flask = None
    jsonify = None

from html2md import __version__

DEFAULT_PORT = 10000

app = Flask(__name__) if Flask is not None else None


if app:
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

    hostname = os.environ.get('HOST', '127.0.0.1')
    if hostname == '0.0.0.0':
        print(
            'Security Warning: Host is set to 0.0.0.0, making the server '
            'accessible from any network interface. Use with caution.'
        )
    return hostname, port_value


if __name__ == '__main__':
    if app is None:
        print('Error: Flask is not installed. Cannot start the development server.')
        exit(1)

    host, port = get_host_port()
    print(
        'WARNING: This is a development server. Do not use it in a production '
        'deployment. Use a production WSGI server instead.'
    )
    app.run(host=host, port=port)
