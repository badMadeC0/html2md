"""Root-level entry point for local development.

Usage:
    python app.py

This script assumes either:
- The package is installed (for example, via `pip install -e .`), or
- You are running from a source checkout where `src/` contains the `html2md` package.
"""
import os
import sys

# Ensure a local `src/` directory (if present) is on sys.path so that
# `html2md` can be imported without requiring an installed package.
_here = os.path.dirname(__file__)
_src_path = os.path.join(_here, "src")
if os.path.isdir(_src_path) and _src_path not in sys.path:
    sys.path.insert(0, _src_path)
from html2md.app import app, get_host_port

if __name__ == '__main__':
    host, port = get_host_port()
    app.run(host=host, port=port)
