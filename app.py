"""Root-level entry point for local development.

Usage:
    python app.py

This script assumes either:
- The package is installed (for example, via `pip install -e .`), or
- You are running from a source checkout where `src/` contains the `html2md` package.
"""
import sys
from pathlib import Path

# Ensure a local `src/` directory (if present) is on sys.path so that
# `html2md` can be imported without requiring an installed package.
_here = Path(__file__).resolve().parent
_src_path = _here / "src"
if _src_path.is_dir():
    resolved_src = str(_src_path)
    if resolved_src not in sys.path:
        sys.path.insert(0, resolved_src)
from html2md.app import app, get_host_port

if __name__ == '__main__':
    host, port = get_host_port()
    app.run(host=host, port=port)
