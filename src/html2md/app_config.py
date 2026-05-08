"""Configuration helpers for the html2md web application."""

import os

DEFAULT_PORT = 10000


def get_host_port():
    """Get host and port from environment variables."""
    port_str = os.environ.get('PORT')
    try:
        port_value = int(port_str) if port_str is not None else DEFAULT_PORT
    except ValueError:
        print(
            f'Warning: Invalid PORT environment variable value '
            f'{port_str!r}; falling back to default {DEFAULT_PORT}.'
        )
        port_value = DEFAULT_PORT

    hostname = os.environ.get('HOST', '0.0.0.0')
    return hostname, port_value
