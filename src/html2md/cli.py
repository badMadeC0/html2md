"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
import socket
import ipaddress
from contextlib import contextmanager
from urllib.parse import urljoin, urlparse, unquote


def _resolve_global_addrinfo(hostname: str, port: int):
    """Resolve a host and return addrinfo only when every answer is global."""
    addrinfo = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)

    if not addrinfo:
        raise socket.gaierror("No addresses found")

    for result in addrinfo:
        try:
            ip_obj = ipaddress.ip_address(result[4][0])
        except (IndexError, ValueError) as exc:
            raise ValueError("Invalid address info") from exc

        if _is_restricted_ip_address(ip_obj):
            return None

    return addrinfo


@contextmanager
def _bound_getaddrinfo(hostname: str, addrinfo):
    """Pin requests' DNS lookup for hostname to previously vetted answers."""
    original_getaddrinfo = socket.getaddrinfo
    normalized_hostname = hostname.rstrip('.').lower()

    def getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if (
            isinstance(host, str)
            and host.rstrip('.').lower() == normalized_hostname
        ):
            return addrinfo
        return original_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = getaddrinfo
    try:
        yield
    finally:
        socket.getaddrinfo = original_getaddrinfo


def _validate_url_for_fetch(target_url: str):
    """Validate a URL and return parsed details plus vetted DNS answers."""
    parsed = urlparse(target_url)
    if parsed.scheme not in ('http', 'https'):
        return parsed, None, (
            f"Error: Unsupported URL scheme '{parsed.scheme}'. "
            "Only http and https are allowed."
        )

    hostname = parsed.hostname
    if not hostname:
        return parsed, None, "Error: URL is missing a hostname."

    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    try:
        addrinfo = _resolve_global_addrinfo(hostname, port)
    except (socket.gaierror, UnicodeEncodeError, ValueError):
        return parsed, None, "Error: Could not resolve hostname to a valid IP."

    if addrinfo is None:
        return parsed, None, (
            "Error: URL resolves to a restricted/private network address."
        )

    return parsed, addrinfo, None


def _get_with_vetted_redirects(session, target_url: str, timeout: int, requests_module):
    """Fetch a URL after validating each redirect and pinning vetted DNS answers."""
    current_url = target_url

    for _ in range(10):
        parsed, addrinfo, error = _validate_url_for_fetch(current_url)
        if error:
            print(error, file=sys.stderr)
            return None

        with _bound_getaddrinfo(parsed.hostname, addrinfo):
            response = session.get(current_url, timeout=timeout, allow_redirects=False)

        if response.is_redirect is not True:
            return response

        redirect_url = response.headers.get('Location')
        if not redirect_url:
            return response
        current_url = urljoin(current_url, redirect_url)

    raise requests_module.TooManyRedirects("Exceeded 10 redirects.")


def _is_restricted_ip_address(
    ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> bool:
    """Return True when an IP address is unsafe for URL fetching."""
    return (
        not ip_obj.is_global
        or ip_obj.is_reserved
        or ip_obj.is_multicast
        or getattr(ip_obj, "is_site_local", False)
    )


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

            _, _, error = _validate_url_for_fetch(target_url)
            if error:
                print(error, file=sys.stderr)
                return

            print(f"Processing URL: {target_url}")

            try:
                print("Fetching content...")
                response = _get_with_vetted_redirects(
                    session, target_url, timeout=30, requests_module=requests
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
