"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
import socket
import ipaddress
from urllib.parse import urlparse, unquote, urljoin

MAX_REDIRECTS = 30
RESTRICTED_NETWORK_ERROR = "Error: URL resolves to a restricted/private network address."
REDIRECT_STATUSES = {301, 302, 303, 307, 308}


def _is_restricted_ip(ip: str) -> bool:
    """Return whether an IP address is unsafe for user-requested fetches."""
    ip_obj = ipaddress.ip_address(ip)
    return (
        not ip_obj.is_global
        or ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_reserved
        or ip_obj.is_unspecified
    )


def _validate_fetch_url(target_url: str) -> None:
    """Validate that a URL is safe to fetch over the network.

    Raises:
        ValueError: If the URL scheme or resolved addresses are unsafe.
        socket.gaierror: If the hostname cannot be resolved.
    """
    parsed = urlparse(target_url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(
            f"Unsupported URL scheme '{parsed.scheme}'. Only http and https are allowed."
        )

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL is missing a hostname.")

    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    resolved_addresses = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    if not resolved_addresses:
        raise socket.gaierror("No addresses found")

    checked_ips = set()
    for result in resolved_addresses:
        ip = result[4][0]
        if ip in checked_ips:
            continue
        checked_ips.add(ip)
        if _is_restricted_ip(ip):
            raise PermissionError(RESTRICTED_NETWORK_ERROR)


def _validated_create_connection(
    address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None, socket_options=None
):
    """Create a socket using only freshly validated public address candidates."""
    host, port = address
    resolved_addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not resolved_addresses:
        raise socket.gaierror("No addresses found")

    for result in resolved_addresses:
        ip = result[4][0]
        if _is_restricted_ip(ip):
            raise PermissionError(RESTRICTED_NETWORK_ERROR)

    err = None
    for result in resolved_addresses:
        family, socktype, proto, _canonname, sockaddr = result
        sock = None
        try:
            sock = socket.socket(family, socktype, proto)
            if socket_options:
                for opt in socket_options:
                    sock.setsockopt(*opt)
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sockaddr)
            return sock
        except OSError as exc:
            err = exc
            if sock is not None:
                sock.close()

    if err is not None:
        raise err
    raise socket.gaierror("No addresses found")


def _fetch_with_validated_redirects(
    session, target_url: str, connection_module, timeout: int = 30
):
    """Fetch a URL, validating every redirect target before following it."""
    current_url = target_url
    for _ in range(MAX_REDIRECTS + 1):
        _validate_fetch_url(current_url)
        original_create_connection = connection_module.create_connection
        connection_module.create_connection = _validated_create_connection
        try:
            response = session.get(current_url, timeout=timeout, allow_redirects=False)
        finally:
            connection_module.create_connection = original_create_connection

        if response.status_code not in REDIRECT_STATUSES:
            return response

        location = response.headers.get('Location')
        response.close()
        if not location:
            return response
        current_url = urljoin(current_url, location)

    raise RuntimeError("Too many redirects while fetching URL.")


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

        import urllib3.util.connection as urllib3_connection  # type: ignore

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

            try:
                _validate_fetch_url(target_url)
            except PermissionError as e:
                print(str(e), file=sys.stderr)
                return
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                return
            except socket.gaierror:
                print("Error: Could not resolve hostname to a valid IP.", file=sys.stderr)
                return

            print(f"Processing URL: {target_url}")

            try:
                print("Fetching content...")
                response = _fetch_with_validated_redirects(
                    session, target_url, urllib3_connection, timeout=30
                )
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

            except PermissionError as e:
                print(str(e), file=sys.stderr)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
            except socket.gaierror:
                print("Error: Could not resolve hostname to a valid IP.", file=sys.stderr)
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
