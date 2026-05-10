"""Non-Flask configuration helpers for html2md."""

from __future__ import annotations

import os

DEFAULT_PORT = 10000


def get_host_port() -> tuple[str, int]:
    """Get host and port from environment variables.

    Returns the HOST env var (default ``'0.0.0.0'``) and PORT env var parsed
    as an integer.  If PORT is absent or not a valid integer, falls back to
    :data:`DEFAULT_PORT` and prints a warning.
    """
    port_str = os.environ.get('PORT')
    if port_str is not None:
        try:
            port_value = int(port_str)
        except ValueError:
            print(
                f"Warning: Invalid PORT environment variable value "
                f"{port_str!r}; falling back to default {DEFAULT_PORT}."
            )
            port_value = DEFAULT_PORT
    else:
        port_value = DEFAULT_PORT

    hostname = os.environ.get('HOST', '0.0.0.0')
    return hostname, port_value
