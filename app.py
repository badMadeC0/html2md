"""Minimal Flask web server for Render deployment and Jules integration."""

import os
from flask import Flask, jsonify
from html2md import __version__

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify(status="ok", version=__version__, service="html2md-cli")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
