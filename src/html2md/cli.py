"""CLI entry point for html2md."""

from __future__ import annotations

import argparse
import ipaddress
import os
import socket
import sys
from contextlib import contextmanager
from typing import Optional
from urllib.parse import unquote, urljoin, urlparse


MAX_REDIRECTS = 10


class UnsafeUrlError(ValueError):
    """Raised when a URL resolves to a non-public network address."""


class UnsafeRedirectError(ValueError):
    """Raised when a redirect points to an unsupported or unsafe URL."""


def _url_port(parsed) -> Optional[int]:
    """Return the explicit or default network port for a parsed URL."""
    if parsed.port is not None:
        return parsed.port
    if parsed.scheme == "https":
        return 443
    if parsed.scheme == "http":
        return 80
    return None


def _global_addr_info(hostname: str, port: Optional[int]):
    """Resolve a hostname and return address records only if all are public."""
    # Resolve hostname to all associated IPv4 and IPv6 addresses. Treat any
    # address that is not globally routable as unsafe, including shared,
    # documentation, benchmarking, private, loopback, and link-local ranges.
    addr_info = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    if not addr_info:
        raise UnsafeUrlError("hostname did not resolve")

    for info in addr_info:
        ip_str = info[4][0]
        ip = ipaddress.ip_address(ip_str)
        if not ip.is_global:
            raise UnsafeUrlError(f"hostname resolved to non-public address {ip}")
    return addr_info


def is_safe_url(url: str) -> bool:
    """Check if the URL resolves only to globally reachable IP addresses."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
        _global_addr_info(hostname, _url_port(parsed))
        return True
    except (socket.gaierror, ValueError):
        # If DNS resolution fails or IP parsing fails, consider it unsafe
        return False


@contextmanager
def _ssrf_safe_connection():
    """Patch urllib3 connection creation to connect only to validated IPs.

    The CLI performs a pre-flight safety check for friendly error messages, but
    the security boundary must be the address used by the actual socket connect.
    Requests/urllib3 normally resolves hostnames inside its connection helper;
    replacing that helper lets us validate the fresh DNS answer and then pin the
    TCP connection to that exact IP address so DNS rebinding cannot swap in a
    private address after the pre-flight check.
    """
    import urllib3.connection  # type: ignore  # pylint: disable=import-outside-toplevel
    import urllib3.util.connection  # type: ignore  # pylint: disable=import-outside-toplevel

    original_util_create_connection = urllib3.util.connection.create_connection
    original_connection_create_connection = getattr(
        urllib3.connection, "create_connection", None
    )

    def create_safe_connection(
        address,
        timeout=socket._GLOBAL_DEFAULT_TIMEOUT,  # pylint: disable=protected-access
        source_address=None,
        socket_options=None,
    ):
        host, port = address
        addr_info = _global_addr_info(host, port)
        last_error = None

        for info in addr_info:
            ip_address = info[4][0]
            try:
                return original_util_create_connection(
                    (ip_address, port),
                    timeout=timeout,
                    source_address=source_address,
                    socket_options=socket_options,
                )
            except OSError as exc:
                last_error = exc

        if last_error is not None:
            raise last_error
        raise UnsafeUrlError("hostname did not resolve to a connectable address")

    urllib3.util.connection.create_connection = create_safe_connection
    if original_connection_create_connection is not None:
        urllib3.connection.create_connection = create_safe_connection
    try:
        yield
    finally:
        urllib3.util.connection.create_connection = original_util_create_connection
        if original_connection_create_connection is not None:
            urllib3.connection.create_connection = original_connection_create_connection


def _safe_session_get(session, target_url: str):
    """Fetch a URL with DNS-pinned connects and manually validated redirects."""
    # Environment-configured proxies perform their own target DNS resolution,
    # which would bypass the DNS pinning enforced by _ssrf_safe_connection().
    # Disable requests' trust in proxy-related environment variables for this
    # SSRF-protected fetch path so the validated socket is the target socket.
    session.trust_env = False

    current_url = target_url
    for _ in range(MAX_REDIRECTS + 1):
        parsed = urlparse(current_url)
        if parsed.scheme not in ("http", "https"):
            raise UnsafeRedirectError(
                f"Redirect target uses unsupported URL scheme '{parsed.scheme}'."
            )
        if not is_safe_url(current_url):
            raise UnsafeUrlError(
                f"URL '{current_url}' resolves to a non-public IP address."
            )

        with _ssrf_safe_connection():
            response = session.get(current_url, timeout=30, allow_redirects=False)

        status_code = getattr(response, "status_code", None)
        location = getattr(response, "headers", {}).get("Location") or getattr(
            response, "headers", {}
        ).get("location")
        if not isinstance(status_code, int) or not (300 <= status_code < 400):
            return response
        if not location:
            return response

        current_url = urljoin(current_url, location)

    raise UnsafeRedirectError("Too many redirects while fetching URL.")


def main(argv=None):  # pylint: disable=too-many-statements
    """Run the CLI."""
    ap = argparse.ArgumentParser(
        prog="html2md", description="Convert HTML URL to Markdown."
    )
    ap.add_argument("--help-only", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--url", help="Input URL to convert")
    ap.add_argument("--batch", help="File containing URLs to process (one per line)")
    ap.add_argument("--outdir", help="Output directory to save the file")

    args = ap.parse_args(argv)

    if args.help_only:
        ap.print_help()
        return 0

    if args.url or args.batch:
        try:
            import requests  # type: ignore  # pylint: disable=import-outside-toplevel
            from markdownify import (
                markdownify as md,
            )  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            print(
                f"Error: Missing dependency {e.name}."
                "Please run: pip install requests markdownify",
                file=sys.stderr,
            )
            return 1

        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,image/apng,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.google.com/",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-User": "?1",
            }
        )

        def process_url(target_url: str) -> None:
            """Process a single URL."""
            # Fix common URL typo: trailing slash before query parameters
            if "/?" in target_url:
                target_url = target_url.replace("/?", "?")

            parsed = urlparse(target_url)
            if parsed.scheme not in ("http", "https"):
                print(
                    f"Error: Unsupported URL scheme '{parsed.scheme}'. "
                    "Only http and https are allowed.",
                    file=sys.stderr,
                )
                return

            print(f"Processing URL: {target_url}")

            if not is_safe_url(target_url):
                print(
                    f"Error: URL '{target_url}' resolves to a non-public IP address.",
                    file=sys.stderr,
                )
                return

            try:
                print("Fetching content...")
                response = _safe_session_get(session, target_url)
                response.raise_for_status()

                print("Converting to Markdown...")
                md_content = md(response.text, heading_style="ATX")

                if args.outdir:
                    if not os.path.exists(args.outdir):
                        os.makedirs(args.outdir)

                    # Create a safe filename based on the URL
                    filename = "conversion_result.md"
                    url_path = target_url.split("?")[0].rstrip("/")
                    if url_path:
                        base = os.path.basename(unquote(url_path))
                        # Sanitize to prevent path traversal
                        base = base.replace("/", "_").replace("\\", "_")
                        base = base.strip(". ")
                        if base:
                            filename = f"{base}.md"

                    out_path = os.path.join(args.outdir, filename)
                    # Final safety check: ensure output stays within outdir
                    real_outdir = os.path.realpath(args.outdir)
                    real_out_path = os.path.realpath(out_path)
                    if os.path.commonpath([real_outdir, real_out_path]) != real_outdir:
                        print(
                            "Error: Output path escapes output directory.",
                            file=sys.stderr,
                        )
                        return
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(md_content)
                    print(f"Success! Saved to: {out_path}")
                else:
                    print(md_content)

            except (UnsafeUrlError, UnsafeRedirectError) as e:
                print(f"Error: {e}", file=sys.stderr)
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
            with open(args.batch, "r", encoding="utf-8") as f:
                for line in f:
                    u = line.strip()
                    if u:
                        process_url(u)

        return 0

    ap.print_help()
    return 0
