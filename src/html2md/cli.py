"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import logging
import os
import sys

def get_unique_filepath(filepath: str) -> str:
    """
    Checks if a file exists. If so, appends a number to the filename
    (before the extension) until a unique name is found.
    """
    if not os.path.exists(filepath):
        return filepath
    
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    
    i = 1
    while True:
        new_name = f"{name} ({i}){ext}"
        new_filepath = os.path.join(directory, new_name)
        if not os.path.exists(new_filepath):
            return new_filepath
        i += 1

def main(argv=None):
    """Run the CLI."""
    # Configure logging to stderr
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        stream=sys.stderr,
    )

    ap = argparse.ArgumentParser(
        prog='html2md',
        description='Convert HTML URL to Markdown.'
    )
    ap.add_argument('--help-only', action='store_true', help=argparse.SUPPRESS)
    ap.add_argument('--url', help='Input URL to convert')
    ap.add_argument('--batch', help='File containing URLs to process (one per line)')
    ap.add_argument('--outdir', help='Output directory to save the file')
    ap.add_argument('--all-formats', action='store_true', help='Output to all formats (md, pdf, txt)')
    ap.add_argument('--main-content', action='store_true', help='Extract only the main content of the page')

    args = ap.parse_args(argv)

    if args.help_only:
        ap.print_help()
        return 0

    if args.url or args.batch:
        try:
            import requests  # type: ignore  # pylint: disable=import-outside-toplevel
            from markdownify import markdownify as md  # pylint: disable=import-outside-toplevel
            from bs4 import BeautifulSoup # pylint: disable=import-outside-toplevel
            from reportlab.platypus import SimpleDocTemplate, Paragraph # pylint: disable=import-outside-toplevel
            from reportlab.lib.styles import getSampleStyleSheet # pylint: disable=import-outside-toplevel
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

        def process_url(target_url: str) -> None:
            """Process a single URL."""
            # Fix common URL typo: trailing slash before query parameters
            if '/?' in target_url:
                target_url = target_url.replace('/?', '?')

            processing_msg = f"Processing URL: {target_url}"
            logging.info(processing_msg)

            try:
                fetch_msg = "Fetching content..."
                logging.info(fetch_msg)
                response = session.get(target_url, timeout=30)
                response.raise_for_status()

                convert_msg = "Converting to Markdown..."
                logging.info(convert_msg)
                md_content = md(response.text, heading_style="ATX")

                if args.outdir:
                    if not os.path.exists(args.outdir):
                        os.makedirs(args.outdir)

                    # Create a base filename from the URL
                    base_filename = "conversion_result"
                    url_path = target_url.split('?')[0].rstrip('/')
                    if url_path:
                        base = os.path.basename(url_path)
                        if base:
                            base_filename = base
                    
                    # --- Save Markdown file ---
                    md_out_path = os.path.join(args.outdir, f"{base_filename}.md")
                    md_out_path = get_unique_filepath(md_out_path)
                    with open(md_out_path, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    logging.info(f"Success! Saved to: {md_out_path}")
                else:
                    print(md_content)

            except Exception as e:  # pylint: disable=broad-exception-caught
                error_msg = f"Conversion failed: {e}"
                logging.error(error_msg)

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
