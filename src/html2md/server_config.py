"""Server configuration helpers for the optional web app."""

from __future__ import annotations

import os

DEFAULT_HOST = '127.0.0.1'
DEPLOY_HOST = '0.0.0.0'
DEFAULT_PORT = 10000


def get_host_port():
    """Get host and port from environment variables.

    Local runs with neither HOST nor PORT set bind to localhost for a
    secure-by-default development experience. Managed web hosts commonly set
    only PORT and expect apps to bind to all interfaces, so preserve that
    deploy-safe default unless HOST is explicitly set.
    """
    port_str = os.environ.get('PORT')
    try:
        port_value = int(port_str) if port_str is not None else DEFAULT_PORT
    except ValueError:
        print(
            f'Warning: Invalid PORT environment variable value '
            f'{port_str!r}; falling back to default {DEFAULT_PORT}.'
        )
        port_value = DEFAULT_PORT

    hostname = os.environ.get('HOST')
    if hostname:
        return hostname, port_value

    if port_str is not None:
        return DEPLOY_HOST, port_value

    return DEFAULT_HOST, port_value
