"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import ipaddress
import logging
import os
import socket
from urllib.parse import urlparse, urljoin

def main(argv=None):
    """Run the CLI."""
    # Configure logging to stderr
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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
            logging.error(f"Missing dependency {e.name}. Please run: pip install requests markdownify")
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

        def validate_url(url: str) -> bool:
            """
            Validate the URL to prevent SSRF attacks.
            Ensures the URL scheme is http/https and the hostname does not resolve to a private IP.
            """
            try:
                parsed = urlparse(url)
                if parsed.scheme not in ('http', 'https'):
                    logging.warning(f"Invalid scheme for URL: {url}")
                    return False

                hostname = parsed.hostname
                if not hostname:
                    return False

                # Check if hostname is an IP address
                try:
                    ip_obj = ipaddress.ip_address(hostname)
                    if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                         logging.warning(f"Blocked private IP: {hostname}")
                         return False
                except ValueError:
                    # Hostname is not an IP, resolve it
                    try:
                        addr_info = socket.getaddrinfo(hostname, None)
                        for _, _, _, _, sockaddr in addr_info:
                            ip = sockaddr[0]
                            ip_obj = ipaddress.ip_address(ip)
                            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                                logging.warning(f"Blocked domain resolving to private IP: {hostname} -> {ip}")
                                return False
                    except socket.gaierror:
                        logging.warning(f"Could not resolve hostname: {hostname}")
                        return False

                return True
            except Exception as e:
                logging.error(f"URL validation error: {e}")
                return False

        def process_url(target_url: str) -> None:
            """Process a single URL."""
            # Fix common URL typo: trailing slash before query parameters
            if '/?' in target_url:
                target_url = target_url.replace('/?', '?')

            logging.info(f"Processing URL: {target_url}")

            try:
                current_url = target_url
                response = None

                # Manual redirect handling with validation
                for _ in range(10):  # Max 10 redirects
                    if not validate_url(current_url):
                        logging.error(f"URL validation failed: {current_url}")
                        return

                    logging.info(f"Fetching content from: {current_url}")
                    response = session.get(current_url, timeout=30, allow_redirects=False)

                    if response.is_redirect:
                        location = response.headers.get('Location')
                        if not location:
                            break

                        # Resolve relative URL
                        prev_url = current_url
                        current_url = urljoin(current_url, location)
                        logging.info(f"Redirecting: {prev_url} -> {current_url}")
                        continue
                    else:
                        break
                else:
                    logging.error("Too many redirects")
                    return

                if response is None:
                    logging.error("No response received")
                    return

                response.raise_for_status()

                logging.info("Converting to Markdown...")
                md_content = md(response.text, heading_style="ATX")

                if args.outdir:
                    if not os.path.exists(args.outdir):
                        os.makedirs(args.outdir)

                    # Create a simple filename based on the URL
                    filename = "conversion_result.md"
                    url_path = target_url.split('?')[0].rstrip('/')
                    if url_path:
                        base = os.path.basename(url_path)
                        if base:
                            filename = f"{base}.md"

                    out_path = os.path.join(args.outdir, filename)
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    logging.info(f"Success! Saved to: {out_path}")
                else:
                    print(md_content)

            except Exception as e:  # pylint: disable=broad-exception-caught
                logging.error(f"Conversion failed: {e}")

        if args.url:
            process_url(args.url)

        if args.batch:
            if not os.path.exists(args.batch):
                logging.error(f"Batch file not found: {args.batch}")
                return 1
            with open(args.batch, 'r', encoding='utf-8') as f:
                for line in f:
                    u = line.strip()
                    if u:
                        process_url(u)

        return 0

    ap.print_help()
    return 0
