"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import html
import os
import sys

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
    ap.add_argument('--all-formats', action='store_true', help='Generate all formats (placeholder)')
    ap.add_argument('--main-content', action='store_true',
                    help='Extract main content only (placeholder)')

    args = ap.parse_args(argv)

    if args.help_only:
        ap.print_help()
        return 0

    if args.url or args.batch:
        try:
            import requests  # type: ignore  # pylint: disable=import-outside-toplevel
            from markdownify import markdownify as md  # pylint: disable=import-outside-toplevel
            from bs4 import BeautifulSoup  # pylint: disable=import-outside-toplevel
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer  # type: ignore  # pylint: disable=import-outside-toplevel
            from reportlab.lib.styles import getSampleStyleSheet  # type: ignore  # pylint: disable=import-outside-toplevel
            from reportlab.lib.pagesizes import letter  # type: ignore  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            print(f"Error: Missing dependency {e.name}."
                  "Please run: pip install requests markdownify beautifulsoup4 reportlab tqdm")
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

        def process_url(target_url: str, quiet: bool = False) -> None:
            """Process a single URL."""
            # Fix common URL typo: trailing slash before query parameters
            if '/?' in target_url:
                target_url = target_url.replace('/?', '?')

            if not quiet:
                print(f"Processing URL: {target_url}")

            try:
                if not quiet:
                    print("Fetching content...")
                response = session.get(target_url, timeout=30)
                response.raise_for_status()

                html_text = response.text

                if args.main_content:
                    soup = BeautifulSoup(html_text, 'html.parser')
                    # Heuristic: main -> article -> #content -> #main
                    content = soup.find('main') or \
                              soup.find('article') or \
                              soup.find(id='content') or \
                              soup.find(id='main')
                    if content:
                        html_text = str(content)

                if not quiet:
                    print("Converting to Markdown...")
                md_content = md(html_text, heading_style="ATX")

                if args.outdir:
                    if not os.path.exists(args.outdir):
                        os.makedirs(args.outdir)

                    # Create a simple filename based on the URL
                    base_name = "conversion_result"
                    url_path = target_url.split('?')[0].rstrip('/')
                    if url_path:
                        base = os.path.basename(url_path)
                        if base:
                            base_name = base

                    # Save Markdown
                    out_path = os.path.join(args.outdir, f"{base_name}.md")
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    if not quiet:
                        print(f"Success! Saved to: {out_path}")

                    if args.all_formats:
                        # Save TXT
                        soup_text = BeautifulSoup(html_text, 'html.parser')
                        txt_content = soup_text.get_text(separator='\n\n')
                        txt_path = os.path.join(args.outdir, f"{base_name}.txt")
                        with open(txt_path, 'w', encoding='utf-8') as f:
                            f.write(txt_content)
                        if not quiet:
                            print(f"Saved TXT: {txt_path}")

                        # Save PDF
                        pdf_path = os.path.join(args.outdir, f"{base_name}.pdf")
                        try:
                            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                            styles = getSampleStyleSheet()
                            story = []
                            for line in txt_content.splitlines():
                                if line.strip():
                                    story.append(
                                        Paragraph(
                                            html.escape(
                                                line.strip()),
                                                styles['Normal']))
                                    story.append(Spacer(1, 6))
                            doc.build(story)
                            if not quiet:
                                print(f"Saved PDF: {pdf_path}")
                        except (OSError, ValueError) as e:
                            msg = f"PDF generation failed for {target_url}: {e}"
                            print(msg, file=sys.stderr)
                else:
                    print(md_content)

            except requests.RequestException as e:
                msg = f"Network error for {target_url}: {e}"
                print(msg, file=sys.stderr)
            except OSError as e:
                msg = f"File error for {target_url}: {e}"
                print(msg, file=sys.stderr)
            except Exception as e:  # pylint: disable=broad-exception-caught
                msg = f"Conversion failed for {target_url}: {e}"
                print(msg, file=sys.stderr)

        if args.url:
            process_url(args.url)

        if args.batch:
            if not os.path.exists(args.batch):
                print(f"Error: Batch file not found: {args.batch}")
                return 1

            with open(args.batch, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]

            for idx, u in enumerate(urls, 1):
                print(f"[{idx}/{len(urls)}] Processing: {os.path.basename(u.split('?')[0])}")
                process_url(u, quiet=True)

        return 0

    ap.print_help()
    return 0
