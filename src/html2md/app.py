import os

from flask import Flask, jsonify

from . import __version__

app = Flask(__name__)


@app.route('/health')
def health():
    """Return the health status of the application."""
    return jsonify({'status': 'ok', 'service': 'html2md', 'version': __version__})


def get_host_port():
    default_port = 10000
    port_str = os.environ.get('PORT')
    try:
        port = int(port_str) if port_str is not None else default_port
    except ValueError:
        print(
            f'Warning: Invalid PORT environment variable value '
            f'{port_str!r}; falling back to default {default_port}.'
        )
        port = default_port

    host = os.environ.get('HOST', '127.0.0.1')
    return host, port


if __name__=='__main__':
    host, port = get_host_port()
    app.run(host=host, port=port)
