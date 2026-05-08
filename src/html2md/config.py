"""Runtime configuration helpers for html2md."""

import os

DEFAULT_PORT = 10000


def get_host_port():
    """Get host and port from environment variables."""
    port_str = os.environ.get('PORT')
    try:
        if port_str is not None:
            port_value = int(port_str)
            if port_value < 1 or port_value > 65535:
                raise ValueError('Port out of range')
        else:
            port_value = DEFAULT_PORT
    except ValueError:
        print(
            f'Warning: Invalid PORT environment variable value '
            f'{port_str!r}; falling back to default {DEFAULT_PORT}.'
        )
        port_value = DEFAULT_PORT

    hostname = os.environ.get('HOST', '0.0.0.0')
    return hostname, port_value
