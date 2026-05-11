"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
from collections.abc import Iterator
from contextlib import contextmanager
import ipaddress
import os
import socket
import sys
from urllib.parse import urlparse, unquote, urljoin


_AddrInfo = tuple[int, int, int, str, tuple]


def _check_ssrf(hostname: str) -> list[_AddrInfo]:
    """Resolve *hostname* and block any non-globally-routable address.

    Uses ``socket.getaddrinfo`` so that every returned address (IPv4 and IPv6)
    is validated, preventing SSRF via dual-stack hosts or unexpected AAAA records.
    The validated address info is returned so the HTTP request can be pinned to
    the same DNS answers that were checked.

    Raises ``ValueError`` if the hostname cannot be resolved or any resolved
    address is not globally routable.
    """
    try:
        results = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError(f"Could not resolve hostname '{hostname}'") from exc
    if not results:
        raise ValueError(f"No addresses found for hostname '{hostname}'")

    validated_results: list[_AddrInfo] = []
    for family, socktype, proto, canon, sockaddr in results:
        ip_str = str(sockaddr[0]).split('%')[0]  # strip IPv6 scope-id (e.g. fe80::1%eth0)
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError as exc:
            raise ValueError(
                f"Could not parse resolved address '{ip_str}' for hostname '{hostname}'"
            ) from exc
        if not ip_obj.is_global or ip_obj.is_multicast:
            raise ValueError(
                f"SSRF blocked: '{hostname}' resolves to non-public address {ip_obj}"
            )
        validated_results.append((family, socktype, proto, canon, sockaddr))

    if not validated_results:
        raise ValueError(f"No usable addresses found for hostname '{hostname}'")
    return validated_results


def _normalize_hostname(hostname: object) -> str:
    """Normalize hostnames for comparing requests' resolver input."""
    if isinstance(hostname, bytes):
        hostname = hostname.decode('idna')
    return str(hostname).rstrip('.').lower()


def _with_requested_port(sockaddr: tuple, port: object) -> tuple:
    """Return *sockaddr* with the port requested by ``getaddrinfo``."""
    requested_port = 0 if port is None else port
    if len(sockaddr) == 2:
        return (sockaddr[0], requested_port)
    return (sockaddr[0], requested_port, *sockaddr[2:])


@contextmanager
def _pin_resolved_addrinfo(hostname: str, addrinfo: list[_AddrInfo]) -> Iterator[None]:
    """Temporarily pin ``getaddrinfo`` for *hostname* to validated answers.

    ``requests``/urllib3 performs its own DNS lookup after SSRF validation.
    During the guarded request, return the already-validated address records for
    the same hostname so DNS rebinding or round-robin changes cannot swap in an
    unchecked private/link-local address between validation and connect.
    """
    original_getaddrinfo = socket.getaddrinfo
    pinned_hostname = _normalize_hostname(hostname)

    def pinned_getaddrinfo(
        host: object,
        port: object,
        family: int = 0,
        type: int = 0,  # pylint: disable=redefined-builtin
        proto: int = 0,
        flags: int = 0,
    ) -> list[_AddrInfo]:
        if _normalize_hostname(host) == pinned_hostname:
            matches = [
                (
                    result_family,
                    result_type,
                    result_proto,
                    canon,
                    _with_requested_port(sockaddr, port),
                )
                for result_family, result_type, result_proto, canon, sockaddr in addrinfo
                if family in (0, result_family)
                and type in (0, result_type)
                and proto in (0, result_proto)
            ]
            if matches:
                return matches
        return original_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = pinned_getaddrinfo
    try:
        yield
    finally:
        socket.getaddrinfo = original_getaddrinfo


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
                # Security: SSRF protection + manual redirect handling
                # Validate all resolved IPs (IPv4 & IPv6) at every redirect hop.
                _MAX_REDIRECTS = 10
                current_url = target_url
                response = None
                for _ in range(_MAX_REDIRECTS + 1):
                    hop_parsed = urlparse(current_url)
                    hop_host = hop_parsed.hostname
                    if not hop_host:
                        print("Error: Invalid URL - missing hostname.", file=sys.stderr)
                        return
                    if hop_parsed.scheme not in ('http', 'https'):
                        print(
                            f"Error: Redirect to unsupported scheme '{hop_parsed.scheme}'.",
                            file=sys.stderr,
                        )
                        return
                    try:
                        validated_addrinfo = _check_ssrf(hop_host)
                    except ValueError as ssrf_err:
                        print(f"Error: {ssrf_err}", file=sys.stderr)
                        return
                    with _pin_resolved_addrinfo(hop_host, validated_addrinfo):
                        response = session.get(
                            current_url, timeout=30, stream=True, allow_redirects=False
                        )
                    if response.status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get('Location', '')
                        if not location:
                            break
                        current_url = urljoin(current_url, location)
                        response.close()
                        continue
                    break
                else:
                    print("Error: Too many redirects.", file=sys.stderr)
                    return

                response.raise_for_status()

                # Security: Stream response and enforce 10MB limit to prevent DoS (OOM)
                max_size = 10 * 1024 * 1024
                try:
                    if int(response.headers.get('Content-Length', 0)) > max_size:
                        print(f"Error: Content-Length exceeds maximum allowed size ({max_size} bytes).", file=sys.stderr)
                        response.close()
                        return
                except ValueError:
                    # Invalid or non-numeric Content-Length: treat as unknown size.
                    # The streaming loop below still enforces max_size.
                    pass

                content_bytes = b""
                for chunk in response.iter_content(chunk_size=8192):
                    content_bytes += chunk
                    if len(content_bytes) > max_size:
                        print(f"Error: Downloaded content exceeds maximum allowed size ({max_size} bytes).", file=sys.stderr)
                        response.close()
                        return
                response._content = content_bytes

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
