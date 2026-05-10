"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
import socket
import ipaddress
from contextlib import contextmanager
from urllib.parse import urljoin, urlparse, unquote

REDIRECT_STATUSES = {301, 302, 303, 307, 308}
MAX_REDIRECTS = 10


def _port_for_url(parsed) -> int:
    """Return the explicit or scheme-default port for a parsed URL."""
    if parsed.port is not None:
        return parsed.port
    return 443 if parsed.scheme == 'https' else 80


def _validated_addrinfo_for_url(target_url: str):
    """Return validated address info for an allowed URL, or None if blocked."""
    parsed = urlparse(target_url)
    if parsed.scheme not in ('http', 'https'):
        print(f"Error: Unsupported URL scheme '{parsed.scheme}'. "
              "Only http and https are allowed.", file=sys.stderr)
        return None

    hostname = parsed.hostname
    if not hostname:
        print("Error: URL must include a hostname.", file=sys.stderr)
        return None

    try:
        addrinfo = socket.getaddrinfo(
            hostname, _port_for_url(parsed), type=socket.SOCK_STREAM
        )
    except socket.gaierror:
        print("Error: Could not resolve hostname to a valid IP.", file=sys.stderr)
        return None

    if not addrinfo:
        print("Error: Could not resolve hostname to a valid IP.", file=sys.stderr)
        return None

    for result in addrinfo:
        ip = result[4][0]
        if '%' in ip:
            ip = ip.split('%', 1)[0]
        try:
            ip_obj = ipaddress.ip_address(ip)
        except ValueError:
            print("Error: Could not resolve hostname to a valid IP.", file=sys.stderr)
            return None
        if (
            not ip_obj.is_global
            or ip_obj.is_multicast
            or getattr(ip_obj, 'is_site_local', False)
        ):
            print(
                "Error: URL resolves to a restricted/private network address.",
                file=sys.stderr,
            )
            return None

    return addrinfo


def _validate_url_target(target_url: str) -> bool:
    """Return True when a URL has an allowed scheme and resolves globally."""
    return _validated_addrinfo_for_url(target_url) is not None


def _addrinfo_with_port(addrinfo, port):
    """Return address info with socket addresses adjusted to the requested port."""
    pinned_addrinfo = []
    for family, socktype, proto, canonname, sockaddr in addrinfo:
        if len(sockaddr) == 2:
            host, _ = sockaddr
            sockaddr = (host, port)
        elif len(sockaddr) == 4:
            host, _, flowinfo, scopeid = sockaddr
            sockaddr = (host, port, flowinfo, scopeid)
        pinned_addrinfo.append((family, socktype, proto, canonname, sockaddr))
    return pinned_addrinfo


@contextmanager
def _pin_dns_resolution(hostname: str, port: int, addrinfo):
    """Force socket lookups for hostname:port to reuse prevalidated addresses."""
    original_getaddrinfo = socket.getaddrinfo

    def pinned_getaddrinfo(host, service, *args, **kwargs):
        if host == hostname and service in (port, str(port)):
            return _addrinfo_with_port(addrinfo, port)
        return original_getaddrinfo(host, service, *args, **kwargs)

    socket.getaddrinfo = pinned_getaddrinfo
    try:
        yield
    finally:
        socket.getaddrinfo = original_getaddrinfo


def _get_with_validated_redirects(
    session, target_url: str, timeout: int, first_validated_addrinfo=None
):
    """Fetch a URL while validating and pinning every redirect target."""
    current_url = target_url
    validated_addrinfo = first_validated_addrinfo
    for _ in range(MAX_REDIRECTS + 1):
        if validated_addrinfo is None:
            validated_addrinfo = _validated_addrinfo_for_url(current_url)
            if validated_addrinfo is None:
                return None

        parsed = urlparse(current_url)
        with _pin_dns_resolution(
            parsed.hostname, _port_for_url(parsed), validated_addrinfo
        ):
            response = session.get(
                current_url, timeout=timeout, allow_redirects=False
            )
        status_code = getattr(response, 'status_code', None)
        if status_code not in REDIRECT_STATUSES:
            return response

        location = response.headers.get('Location')
        if not location:
            return response

        current_url = urljoin(current_url, location)
        validated_addrinfo = None

    print("Error: Too many redirects.", file=sys.stderr)
    return None


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

            validated_addrinfo = _validated_addrinfo_for_url(target_url)
            if validated_addrinfo is None:
                return

            print(f"Processing URL: {target_url}")

            try:
                print("Fetching content...")
                response = _get_with_validated_redirects(
                    session,
                    target_url,
                    timeout=30,
                    first_validated_addrinfo=validated_addrinfo,
                )
                if response is None:
                    return
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
