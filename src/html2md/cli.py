"""CLI entry point for html2md."""

from __future__ import annotations
import argparse

def main(argv=None):
    """Run the CLI."""
    ap = argparse.ArgumentParser(
        prog='html2md',
        description=(
            'html2md full CLI not embedded in this environment. '
            'Runtime features require the prior package build.'
        ),
    )
    ap.add_argument('--help-only', action='store_true')
    ap.parse_args(argv)
    print(
        'html2md placeholder: CLI help available, full runtime present in '
        'packaged zip delivered earlier.'
    )
    return 0
