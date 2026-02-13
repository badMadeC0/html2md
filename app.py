"""Root-level entry point for local development.

Usage:
    python app.py
"""
from html2md.app import app, get_host_port

if __name__ == '__main__':
    host, port = get_host_port()
    app.run(host=host, port=port)
