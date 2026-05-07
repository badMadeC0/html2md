"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
import socket
import ipaddress
from urllib.parse import urljoin, urlparse, unquote


def is_safe_url(url: str) -> bool:
    """Check if the URL resolves to a safe, public IP address."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve hostname to all associated IPs
        # This handles IPv4 and IPv6
        addr_info = socket.getaddrinfo(hostname, None)

        for info in addr_info:
            ip_str = info[4][0]
            ip = ipaddress.ip_address(ip_str)
            # Require globally reachable IPs only, while explicitly rejecting
            # multicast addresses because Python 3.12 may report them as global.
            if not ip.is_global or ip.is_multicast:
                return False
        return True
    except (socket.gaierror, ValueError):
        # If DNS resolution fails or IP parsing fails, consider it unsafe
        return False


def fetch_with_safe_redirects(session, url: str, timeout: int, max_redirects: int = 10):
    """Fetch URL while validating every redirect hop against SSRF rules."""
    try:
        import requests  # type: ignore  # pylint: disable=import-outside-toplevel
    except ImportError:  # pragma: no cover
        raise

    current_url = url
    for _ in range(max_redirects + 1):
        if not is_safe_url(current_url):
            raise requests.RequestException(
                f"URL '{current_url}' resolves to a non-public IP address."
            )

        response = session.get(current_url, timeout=timeout, allow_redirects=False)

        status_code = getattr(response, "status_code", 0)
        if not isinstance(status_code, int):
            status_code = 0
        is_redirect = 300 <= status_code < 400
        if not is_redirect:
            return response

        headers = getattr(response, "headers", {}) or {}
        location = headers.get("Location") if hasattr(headers, "get") else None
        if not isinstance(location, str) or not location:
            return response
        current_url = urljoin(current_url, location)

    raise requests.TooManyRedirects(f"Exceeded {max_redirects} redirects for URL: {url}")


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

            try:
                print("Fetching content...")
                response = fetch_with_safe_redirects(session, target_url, timeout=30)
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

            except requests.RequestException as e:
                error_message = str(e)
                if "resolves to a non-public IP address" in error_message:
                    print(f"Error: {error_message}", file=sys.stderr)
                else:
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
