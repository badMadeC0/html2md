"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
import socket
import ipaddress
from functools import partial
from urllib.parse import urljoin, urlparse, unquote

_RESTRICTED_ADDRESS_ERROR = "Error: URL resolves to a restricted/private network address."
_RESOLUTION_ERROR = "Error: Could not resolve hostname to a valid IP."
_MAX_REDIRECTS = 10


class _UrlValidationError(ValueError):
    """Raised when a user-supplied URL fails SSRF validation."""


def _is_allowed_public_ip(ip: str) -> bool:
    """Return whether an IP address is safe for user-requested outbound fetches."""
    ip_obj = ipaddress.ip_address(ip)
    return (
        ip_obj.is_global
        and not ip_obj.is_private
        and not ip_obj.is_loopback
        and not ip_obj.is_link_local
        and not ip_obj.is_multicast
        and not ip_obj.is_reserved
        and not ip_obj.is_unspecified
    )


def _normalize_hostname_for_dns_pin(hostname: str) -> str:
    """Normalize hostnames to the IDNA form used by urllib3 before connecting."""
    return str(hostname).rstrip('.').lower().encode('idna').decode('ascii').lower()


def _resolve_vetted_addresses(hostname: str, port: int):
    """Resolve all stream addresses for hostname and reject any non-public result."""
    addrinfos = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    if not addrinfos:
        raise ValueError("No addresses found")

    vetted = []
    seen = set()
    for family, socktype, proto, canonname, sockaddr in addrinfos:
        ip = sockaddr[0]
        if not _is_allowed_public_ip(ip):
            raise ValueError("Restricted address")

        key = (family, socktype, proto, canonname, sockaddr)
        if key not in seen:
            seen.add(key)
            vetted.append((family, socktype, proto, canonname, sockaddr))

    return vetted


def _validate_url_target(target_url: str):
    """Validate a URL and return parsed URL plus DNS answers pinned to public IPs."""
    parsed = urlparse(target_url)
    if parsed.scheme not in ('http', 'https'):
        raise _UrlValidationError(
            f"Error: Unsupported URL scheme '{parsed.scheme}'. Only http and https are allowed."
        )

    hostname = parsed.hostname
    if not hostname:
        raise _UrlValidationError("Error: URL must include a hostname.")

    try:
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    except ValueError as exc:
        raise _UrlValidationError("Error: URL contains an invalid port.") from exc
    return parsed, _resolve_vetted_addresses(hostname, port)


def _build_pinned_dns_adapter(vetted_addrinfos):
    """Build a requests adapter whose connections use pre-vetted DNS answers."""
    from requests.adapters import HTTPAdapter  # pylint: disable=import-outside-toplevel

    from urllib3 import PoolManager  # pylint: disable=import-outside-toplevel
    from urllib3.connection import (  # pylint: disable=import-outside-toplevel
        HTTPConnection,
        HTTPSConnection,
    )
    from urllib3.connectionpool import (  # pylint: disable=import-outside-toplevel
        HTTPConnectionPool,
        HTTPSConnectionPool,
    )
    from urllib3.poolmanager import (  # pylint: disable=import-outside-toplevel
        PoolKey,
        _default_key_normalizer,
    )
    from urllib3.exceptions import NewConnectionError  # pylint: disable=import-outside-toplevel
    from urllib3.util.connection import _set_socket_options  # pylint: disable=import-outside-toplevel

    pinned_addrinfos = tuple(vetted_addrinfos)

    class _PinnedConnectionMixin:
        """Open sockets against vetted addresses without changing global DNS."""

        def __init__(self, *args, pinned_addrinfos=None, **kwargs):
            self._pinned_addrinfos = tuple(pinned_addrinfos or ())
            super().__init__(*args, **kwargs)

        def _new_conn(self):
            err = None
            for family, socktype, proto, _canonname, sockaddr in self._pinned_addrinfos:
                sock = None
                try:
                    sock = socket.socket(family, socktype, proto)
                    _set_socket_options(sock, self.socket_options)
                    sock.settimeout(self.timeout)
                    if self.source_address:
                        sock.bind(self.source_address)
                    sock.connect(sockaddr)
                    return sock
                except OSError as exc:
                    err = exc
                    if sock is not None:
                        sock.close()

            message = "getaddrinfo returned an empty list" if err is None else str(err)
            raise NewConnectionError(
                self,
                f"Failed to establish a new connection to a vetted address: {message}",
            ) from err

    class _PinnedHTTPConnection(_PinnedConnectionMixin, HTTPConnection):
        pass

    class _PinnedHTTPSConnection(_PinnedConnectionMixin, HTTPSConnection):
        pass

    class _PinnedHTTPConnectionPool(HTTPConnectionPool):
        ConnectionCls = _PinnedHTTPConnection

    class _PinnedHTTPSConnectionPool(HTTPSConnectionPool):
        ConnectionCls = _PinnedHTTPSConnection

    def _pinned_key_normalizer(key_class, request_context):
        context = request_context.copy()
        context.pop("pinned_addrinfos", None)
        return _default_key_normalizer(key_class, context)

    class _PinnedPoolManager(PoolManager):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pool_classes_by_scheme = {
                "http": _PinnedHTTPConnectionPool,
                "https": _PinnedHTTPSConnectionPool,
            }
            self.key_fn_by_scheme = {
                "http": partial(_pinned_key_normalizer, PoolKey),
                "https": partial(_pinned_key_normalizer, PoolKey),
            }

    class _PinnedDNSAdapter(HTTPAdapter):
        def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
            pool_kwargs["pinned_addrinfos"] = pinned_addrinfos
            self.poolmanager = _PinnedPoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                **pool_kwargs,
            )

    return _PinnedDNSAdapter()


def _get_with_pinned_dns(session, target_url: str, parsed, vetted_addrinfos, timeout: int):
    """Fetch a URL through per-connection sockets bound to vetted DNS answers."""
    import requests  # type: ignore  # pylint: disable=import-outside-toplevel

    pinned_session = requests.Session()
    pinned_session.trust_env = False
    pinned_session.headers.update(session.headers)
    pinned_session.cookies.update(session.cookies)
    pinned_session.mount(f"{parsed.scheme}://", _build_pinned_dns_adapter(vetted_addrinfos))
    return pinned_session.get(target_url, timeout=timeout, allow_redirects=False)


def _safe_get(session, target_url: str, timeout: int = 30):
    """Fetch a URL after validating and pinning each redirect hop's DNS answers."""
    current_url = target_url
    for _ in range(_MAX_REDIRECTS + 1):
        try:
            parsed, vetted_addrinfos = _validate_url_target(current_url)
        except socket.gaierror as exc:
            raise _UrlValidationError(_RESOLUTION_ERROR) from exc
        except _UrlValidationError:
            raise
        except ValueError as exc:
            error = (
                _RESOLUTION_ERROR
                if "No addresses found" in str(exc)
                else _RESTRICTED_ADDRESS_ERROR
            )
            raise _UrlValidationError(error) from exc

        response = _get_with_pinned_dns(session, current_url, parsed, vetted_addrinfos, timeout)
        if getattr(response, 'is_redirect', False) is not True:
            return response

        location = response.headers.get('Location')
        if not location:
            return response
        response.close()
        current_url = urljoin(current_url, location)

    raise _UrlValidationError("Error: Too many redirects.")


def main(argv=None):
    """Run the CLI."""
    ap = argparse.ArgumentParser(
        prog='html2md',
        description='Convert HTML URL to Markdown.'
    )
    ap.add_argument('--help-only', action='store_true', help=argparse.SUPPRESS)
    ap.add_argument('--url', help='Input URL to convert')
    ap.add_argument('--batch', help='File containing URLs to process (one per line)')
    ap.add_argument('--outdir', help='Output directory to save the file')

    args = ap.parse_args(argv)

    if args.help_only:
        ap.print_help()
        return 0

    if args.url or args.batch:
        try:
            import requests  # type: ignore  # pylint: disable=import-outside-toplevel
            from markdownify import markdownify as md  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            print(f"Error: Missing dependency {e.name}."
                  "Please run: pip install requests markdownify", file=sys.stderr)
            return 1

        session = requests.Session()
        session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/avif,image/webp,image/apng,*/*;q=0.8'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
        })

        def process_url(target_url: str) -> None:
            """Process a single URL."""
            # Fix common URL typo: trailing slash before query parameters
            if '/?' in target_url:
                target_url = target_url.replace('/?', '?')

            parsed = urlparse(target_url)
            if parsed.scheme not in ('http', 'https'):
                print(f"Error: Unsupported URL scheme '{parsed.scheme}'. "
                      "Only http and https are allowed.", file=sys.stderr)
                return

            print(f"Processing URL: {target_url}")

            try:
                print("Fetching content...")
                response = _safe_get(session, target_url, timeout=30)
                response.raise_for_status()

                print("Converting to Markdown...")
                md_content = md(response.text, heading_style="ATX")

                if args.outdir:
                    if not os.path.exists(args.outdir):
                        os.makedirs(args.outdir)

                    # Create a safe filename based on the URL
                    filename = "conversion_result.md"
                    url_path = target_url.split('?')[0].rstrip('/')
                    if url_path:
                        base = os.path.basename(unquote(url_path))
                        # Sanitize to prevent path traversal
                        base = base.replace('/', '_').replace('\\', '_')
                        base = base.strip('. ')
                        if base:
                            filename = f"{base}.md"

                    out_path = os.path.join(args.outdir, filename)
                    # Final safety check: ensure output stays within outdir
                    real_outdir = os.path.realpath(args.outdir)
                    real_out_path = os.path.realpath(out_path)
                    if os.path.commonpath([real_outdir, real_out_path]) != real_outdir:
                        print("Error: Output path escapes output directory.",
                              file=sys.stderr)
                        return
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    print(f"Success! Saved to: {out_path}")
                else:
                    print(md_content)

            except _UrlValidationError as e:
                print(str(e), file=sys.stderr)
            except requests.RequestException as e:
                print(f"Network error: {e}", file=sys.stderr)
            except OSError as e:
                print(f"File error: {e}", file=sys.stderr)
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Conversion failed: {e}", file=sys.stderr)

        if args.url:
            process_url(args.url)

        if args.batch:
            if not os.path.exists(args.batch):
                print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
                return 1
            with open(args.batch, 'r', encoding='utf-8') as f:
                for line in f:
                    u = line.strip()
                    if u:
                        process_url(u)

        return 0

    ap.print_help()
    return 0
