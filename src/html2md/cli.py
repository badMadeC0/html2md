"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
import socket
import ipaddress
from contextlib import contextmanager
from urllib.parse import urlparse, unquote, urljoin

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

        def _url_port(parsed):
            """Return the explicit or default network port for a parsed URL."""
            try:
                if parsed.port is not None:
                    return parsed.port
            except ValueError as e:
                print(f"Error: Invalid URL port: {e}", file=sys.stderr)
                return None

            if parsed.scheme == 'http':
                return 80
            if parsed.scheme == 'https':
                return 443
            return None

        def _is_unsafe_ip(ip_obj):
            """Return whether an IP address should be blocked for SSRF protection."""
            return (ip_obj.is_private or ip_obj.is_loopback or
                    ip_obj.is_link_local or ip_obj.is_unspecified or
                    ip_obj.is_reserved or ip_obj.is_multicast)

        def validate_url(target_url: str):
            """Validate a URL and return the DNS answers approved for fetching it."""
            parsed = urlparse(target_url)
            if parsed.scheme not in ('http', 'https'):
                print(f"Error: Unsupported URL scheme '{parsed.scheme}'. "
                      "Only http and https are allowed.", file=sys.stderr)
                return None

            hostname = parsed.hostname
            if not hostname:
                print("Error: Invalid URL.", file=sys.stderr)
                return None

            port = _url_port(parsed)
            if port is None:
                return None

            try:
                # SSRF Protection: Resolve and validate every IP for this host.
                # The approved DNS answers are returned and pinned for the
                # matching request so a second lookup cannot rebind to an
                # internal address after validation.
                addr_info = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
                if not addr_info:
                    print("Error: Hostname did not resolve to any addresses.", file=sys.stderr)
                    return None

                for addr in addr_info:
                    ip_obj = ipaddress.ip_address(addr[4][0])
                    if _is_unsafe_ip(ip_obj):
                        print(f"Error: Unsafe URL pointing to internal IP '{ip_obj}'.", file=sys.stderr)
                        return None
            except Exception as e:
                print(f"Error validating hostname: {e}", file=sys.stderr)
                return None

            return hostname, port, addr_info

        @contextmanager
        def _pin_validated_dns(hostname, port, addr_info):
            """Pin requests DNS resolution to the already-validated answers."""
            original_getaddrinfo = socket.getaddrinfo
            pinned_hostname = hostname.rstrip('.').lower()

            def pinned_getaddrinfo(host, requested_port, family=0, type=0, proto=0, flags=0):
                if host and host.rstrip('.').lower() == pinned_hostname:
                    resolved_port = requested_port if requested_port is not None else port
                    pinned = []
                    for family_, type_, proto_, canonname, sockaddr in addr_info:
                        if family and family_ != family:
                            continue
                        if type and type_ != type:
                            continue
                        if proto and proto_ != proto:
                            continue

                        if len(sockaddr) == 2:
                            pinned_sockaddr = (sockaddr[0], resolved_port)
                        else:
                            pinned_sockaddr = (sockaddr[0], resolved_port, *sockaddr[2:])
                        pinned.append((family_, type_, proto_, canonname, pinned_sockaddr))

                    if pinned:
                        return pinned
                    raise socket.gaierror(
                        f"No pinned DNS answers match requested socket parameters for {host}"
                    )

                return original_getaddrinfo(host, requested_port, family, type, proto, flags)

            socket.getaddrinfo = pinned_getaddrinfo
            try:
                yield
            finally:
                socket.getaddrinfo = original_getaddrinfo

        def fetch_validated_url(target_url: str):
            """Fetch a URL while validating each redirect target before following."""
            current_url = target_url
            max_redirects = 10
            redirect_statuses = (301, 302, 303, 307, 308)

            for _ in range(max_redirects):
                validation = validate_url(current_url)
                if validation is None:
                    return None
                hostname, port, addr_info = validation

                with _pin_validated_dns(hostname, port, addr_info):
                    response = session.get(current_url, timeout=30, allow_redirects=False)
                status_code = getattr(response, 'status_code', None)
                if status_code not in redirect_statuses:
                    return response

                location = response.headers.get('Location') if response.headers else None
                if not location:
                    print(f"Error: Redirect response missing Location header for {current_url}.", file=sys.stderr)
                    return None

                current_url = urljoin(current_url, location)

            print("Error: Too many redirects.", file=sys.stderr)
            return None

        def process_url(target_url: str) -> None:
            """Process a single URL."""
            # Fix common URL typo: trailing slash before query parameters
            if '/?' in target_url:
                target_url = target_url.replace('/?', '?')

            print(f"Processing URL: {target_url}")

            try:
                print("Fetching content...")
                response = fetch_validated_url(target_url)
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
