"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import ipaddress
import os
import socket
import sys
from urllib.parse import urlparse, unquote


def is_safe_url(url: str) -> bool:
    """Check if the URL points to an internal/private network to prevent SSRF."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False

        if hostname.lower() == 'localhost':
            return False

        try:
            # Handle both IPv4 and IPv6 resolution
            addr_info = socket.getaddrinfo(hostname, None)
            for res in addr_info:
                af, socktype, proto, canonname, sa = res
                ip = sa[0]
                # If it's IPv6, remove the scope ID if present (e.g. fe80::1%eth0)
                if "%" in ip:
                    ip = ip.split("%")[0]
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                    return False
        except socket.gaierror:
            return False

        return True
    except Exception:
        return False


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

            if not is_safe_url(target_url):
                print("Error: Access to internal or private networks is not allowed.", file=sys.stderr)
                return

            print(f"Processing URL: {target_url}")

            try:
                print("Fetching content...")
                # Security: Stream response and enforce 10MB limit to prevent DoS (OOM)
                response = session.get(target_url, timeout=30, stream=True)
                response.raise_for_status()

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
