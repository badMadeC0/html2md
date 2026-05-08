"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
from urllib.parse import urlparse, unquote


def _safe_markdown_filename(target_url: str) -> str:
    """Build a contained Markdown filename from a URL."""
    filename = "conversion_result.md"
    url_path = target_url.split('?')[0].rstrip('/')
    if url_path:
        base = os.path.basename(unquote(url_path))
        # Sanitize to prevent path traversal
        base = base.replace('/', '_').replace('\\', '_')
        base = base.strip('. ')
        if base:
            filename = f"{base}.md"
    return filename


def _ensure_contained(outdir: str, out_path: str) -> bool:
    """Return True when out_path stays within outdir."""
    real_outdir = os.path.realpath(outdir)
    real_out_path = os.path.realpath(out_path)
    return os.path.commonpath([real_outdir, real_out_path]) == real_outdir


def _extract_main_content(html: str) -> str:
    """Extract likely main-page content, falling back to the full document."""
    try:
        from bs4 import BeautifulSoup  # type: ignore  # pylint: disable=import-outside-toplevel
    except ImportError:
        return html

    soup = BeautifulSoup(html, "html.parser")
    selectors = [
        "main",
        "article",
        "[role='main']",
        "#main",
        "#content",
        ".main",
        ".content",
    ]
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return str(element)
    return html


def _write_pdf(path: str, text: str) -> bool:
    """Write a simple PDF rendering of text. Return False if ReportLab is unavailable."""
    try:
        from reportlab.lib.pagesizes import letter  # type: ignore  # pylint: disable=import-outside-toplevel
        from reportlab.pdfgen import canvas  # type: ignore  # pylint: disable=import-outside-toplevel
    except ImportError:
        return False

    pdf = canvas.Canvas(path, pagesize=letter)
    _width, height = letter
    y = height - 72
    text_obj = pdf.beginText(72, y)
    text_obj.setFont("Helvetica", 10)

    for line in text.splitlines() or [""]:
        # Keep long Markdown lines readable in a basic PDF without requiring extra deps.
        chunks = [line[i:i + 95] for i in range(0, len(line), 95)] or [""]
        for chunk in chunks:
            if text_obj.getY() < 72:
                pdf.drawText(text_obj)
                pdf.showPage()
                text_obj = pdf.beginText(72, height - 72)
                text_obj.setFont("Helvetica", 10)
            text_obj.textLine(chunk)

    pdf.drawText(text_obj)
    pdf.save()
    return True


def _write_outputs(outdir: str, filename: str, md_content: str, all_formats: bool) -> None:
    """Write conversion output files."""
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    out_path = os.path.join(outdir, filename)
    # Final safety check: ensure output stays within outdir
    if not _ensure_contained(outdir, out_path):
        print("Error: Output path escapes output directory.", file=sys.stderr)
        return

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Success! Saved to: {out_path}")

    if not all_formats:
        return

    root, _ext = os.path.splitext(out_path)
    txt_path = f"{root}.txt"
    pdf_path = f"{root}.pdf"

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Success! Saved to: {txt_path}")

    if _write_pdf(pdf_path, md_content):
        print(f"Success! Saved to: {pdf_path}")
    else:
        print("Warning: ReportLab is not installed; skipped PDF output.", file=sys.stderr)


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
        help='When used with --outdir, save Markdown, TXT, and PDF outputs.'
    )
    ap.add_argument(
        '--main-content',
        action='store_true',
        help='Prefer the page main/article content before converting.'
    )

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
                response = session.get(target_url, timeout=30)
                response.raise_for_status()

                print("Converting to Markdown...")
                html = response.text
                if args.main_content:
                    html = _extract_main_content(html)
                md_content = md(html, heading_style="ATX")

                if args.outdir:
                    filename = _safe_markdown_filename(target_url)
                    _write_outputs(args.outdir, filename, md_content, args.all_formats)
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
