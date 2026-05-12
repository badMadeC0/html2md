"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
import socket
import ipaddress
import idna
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
    normalized = str(hostname).rstrip('.').lower()
    try:
        ipaddress.ip_address(normalized)
    except ValueError:
        return idna.encode(normalized, strict=True, std3_rules=True).decode('ascii')
    return normalized


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
    normalized_hostname = _normalize_hostname_for_dns_pin(hostname)
    return parsed, _resolve_vetted_addresses(normalized_hostname, port)


def _get_with_pinned_dns(session, target_url: str, parsed, vetted_addrinfos, timeout: int):
    """Fetch a URL while forcing socket resolution to reuse vetted DNS answers."""
    original_getaddrinfo = socket.getaddrinfo
    hostname = _normalize_hostname_for_dns_pin(parsed.hostname)
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)

    def pinned_getaddrinfo(host, request_port, family=0, type=0, proto=0, flags=0):
        try:
            request_port_matches = request_port is None or int(request_port) == port
        except (TypeError, ValueError):
            request_port_matches = False

        if (
            _normalize_hostname_for_dns_pin(host) == hostname
            and request_port_matches
        ):
            return [
                addrinfo for addrinfo in vetted_addrinfos
                if (family in (0, addrinfo[0]) and type in (0, addrinfo[1]) and
                    proto in (0, addrinfo[2]))
            ]
        return original_getaddrinfo(host, request_port, family, type, proto, flags)

    socket.getaddrinfo = pinned_getaddrinfo
    try:
        return session.get(target_url, timeout=timeout, allow_redirects=False)
    finally:
        socket.getaddrinfo = original_getaddrinfo


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
            raise _UrlValidationError(_RESTRICTED_ADDRESS_ERROR) from exc

        response = _get_with_pinned_dns(session, current_url, parsed, vetted_addrinfos, timeout)
        if getattr(response, 'is_redirect', False) is not True:
            return response

        location = response.headers.get('Location')
        if not location:
            return response
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
