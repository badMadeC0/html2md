"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
from urllib.parse import urlparse, unquote

import requests  # type: ignore[import-untyped]
from bs4 import BeautifulSoup  # type: ignore[import-untyped]
from markdownify import markdownify as md  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import letter  # type: ignore[import-untyped]
from reportlab.pdfgen import canvas  # type: ignore[import-untyped]

# Keep argparse parser construction independent from locale catalog file access.
argparse._ = lambda message: message  # type: ignore[attr-defined]  # pylint: disable=protected-access

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
    ap.add_argument(
        '--all-formats',
        action='store_true',
        help='Save Markdown, plain text, and PDF outputs when --outdir is used',
    )
    ap.add_argument(
        '--main-content',
        action='store_true',
        help='Prefer the page main/article content instead of the full HTML document',
    )

    args = ap.parse_args(argv)

    if args.help_only:
        ap.print_help()
        return 0

    if args.url or args.batch:
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

        def extract_main_content(html_text: str) -> str:
            """Return likely main content HTML when available."""
            if not args.main_content:
                return html_text

            soup = BeautifulSoup(html_text, 'html.parser')
            main_node = (
                soup.find('main')
                or soup.find('article')
                or soup.find(attrs={'role': 'main'})
                or soup.body
            )
            return str(main_node) if main_node else html_text

        def write_all_formats(base_path: str, markdown_content: str, html_text: str) -> None:
            """Write optional plain text and PDF outputs alongside Markdown."""
            text_content = BeautifulSoup(html_text, 'html.parser').get_text('\n')

            txt_path = f"{base_path}.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"Success! Saved to: {txt_path}")

            pdf_path = f"{base_path}.pdf"
            pdf = canvas.Canvas(pdf_path, pagesize=letter)
            _width, height = letter
            text = pdf.beginText(40, height - 40)
            text.setFont('Helvetica', 10)
            for line in text_content.splitlines():
                for start in range(0, len(line), 95):
                    text.textLine(line[start:start + 95])
                    if text.getY() < 40:
                        pdf.drawText(text)
                        pdf.showPage()
                        text = pdf.beginText(40, height - 40)
                        text.setFont('Helvetica', 10)
            pdf.drawText(text)
            pdf.save()
            print(f"Success! Saved to: {pdf_path}")

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
                response = session.get(target_url, timeout=30)
                response.raise_for_status()

                html_content = extract_main_content(response.text)

                print("Converting to Markdown...")
                md_content = md(html_content, heading_style="ATX")

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

                    stem = os.path.splitext(filename)[0]
                    out_path = os.path.join(args.outdir, filename)
                    base_path = os.path.join(args.outdir, stem)
                    # Final safety check: ensure outputs stay within outdir
                    real_outdir = os.path.realpath(args.outdir)
                    output_paths = [out_path]
                    if args.all_formats:
                        output_paths.extend([f"{base_path}.txt", f"{base_path}.pdf"])
                    if any(
                        os.path.commonpath([real_outdir, os.path.realpath(path)])
                        != real_outdir
                        for path in output_paths
                    ):
                        print("Error: Output path escapes output directory.",
                              file=sys.stderr)
                        return
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    print(f"Success! Saved to: {out_path}")
                    if args.all_formats:
                        write_all_formats(base_path, md_content, html_content)
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
