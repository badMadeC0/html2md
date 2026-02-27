"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import logging
import os
from urllib.parse import urlparse

# Configure module-level logger
logger = logging.getLogger(__name__)

def process_url(target_url: str, session, md_func, outdir: str | None = None) -> None:
    """Process a single URL.

    Args:
        target_url: The URL to process.
        session: The requests session to use.
        md_func: The markdownify function to use.
        outdir: Output directory (optional).
    """
    try:
        # Fix common URL typo: trailing slash before query parameters
        if '/?' in target_url:
            target_url = target_url.replace('/?', '?')

        logger.info("Processing URL: %s", target_url)

        # Validate URL scheme (Security Fix)
        parsed = urlparse(target_url)
        if parsed.scheme.lower() != "https":
            logger.error("Invalid URL scheme '%s' for URL: %s", parsed.scheme, target_url)
            return

        response = session.get(target_url, timeout=30)
        response.raise_for_status()

        logger.info("Converting to Markdown...")
        md_content = md_func(response.text, heading_style="ATX")

        if outdir:
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            # Create a simple filename based on the URL
            filename = "conversion_result.md"
            url_path = target_url.split('?')[0].rstrip('/')
            if url_path:
                base = os.path.basename(url_path)
                if base:
                    filename = f"{base}.md"

            out_path = os.path.join(outdir, filename)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info("Success! Saved to: %s", out_path)
        else:
            print(md_content)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Conversion failed: %s", e)

def main(argv=None):
    """Run the CLI."""
    # Configure logging for the application
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
            logger.error("Error: Missing dependency %s. Please run: pip install requests markdownify", e.name)
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

        if args.url:
            process_url(args.url, session, md, args.outdir)

        if args.batch:
            if not os.path.exists(args.batch):
                logger.error("Error: Batch file not found: %s", args.batch)
                return 1
            with open(args.batch, 'r', encoding='utf-8') as f:
                for line in f:
                    u = line.strip()
                    if u:
                        process_url(u, session, md, args.outdir)

        return 0

    ap.print_help()
    return 0
