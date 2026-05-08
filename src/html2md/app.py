"""Flask application for html2md."""

from flask import Flask, jsonify

from html2md import __version__
from html2md import server_config

DEFAULT_PORT = server_config.DEFAULT_PORT
get_host_port = server_config.get_host_port

app = Flask(__name__)


@app.route('/health')
def health():
    """Return health status of the application."""
    return jsonify({'status': 'ok', 'service': 'html2md', 'version': __version__})


if __name__ == '__main__':
    host, port = get_host_port()
    app.run(host=host, port=port)
