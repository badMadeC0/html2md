"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os

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
            print(f"Error: Missing dependency {e.name}."
                  "Please run: pip install requests markdownify beautifulsoup4 reportlab")
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

            print(f"Processing URL: {target_url}")

            try:
                print("Fetching content...")
                response = session.get(target_url, timeout=30)
                response.raise_for_status()

                html_content = response.text
                if args.main_content:
                    print("Extracting main content...")
                    soup = BeautifulSoup(html_content, 'html.parser')
                    main_tag = soup.find('main')
                    if main_tag:
                        html_content = str(main_tag)
                    else:
                        print("Warning: <main> tag not found, converting entire <body>.")

                print("Converting to Markdown...")
                # Consider using a dedicated sanitizer like bleach or an allow-list of tags
                md_content = md(
                    response.text,
                    heading_style="ATX",
                    strip=['script', 'style', 'iframe', 'object', 'embed', 'link', 'meta', 'svg', 'math', 'form', 'input', 'button']
                )

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
                    print(f"Success! Saved Markdown to: {md_out_path}")

                    if args.all_formats:
                        # --- Save TXT file ---
                        soup = BeautifulSoup(html_content, 'html.parser')
                        text_content = soup.get_text(separator='\n', strip=True)
                        txt_out_path = os.path.join(args.outdir, f"{base_filename}.txt")
                        txt_out_path = get_unique_filepath(txt_out_path)
                        with open(txt_out_path, 'w', encoding='utf-8') as f:
                            f.write(text_content)
                        print(f"Success! Saved TXT to: {txt_out_path}")

                        # --- Save PDF file ---
                        pdf_out_path = os.path.join(args.outdir, f"{base_filename}.pdf")
                        pdf_out_path = get_unique_filepath(pdf_out_path)
                        doc = SimpleDocTemplate(pdf_out_path)
                        styles = getSampleStyleSheet()
                        style = styles['Normal']
                        
                        paragraphs = [Paragraph(p, style) for p in text_content.split('\n') if p.strip()]
                        if not paragraphs:
                            paragraphs = [Paragraph("No content found.", style)]
                        
                        doc.build(paragraphs)
                        print(f"Success! Saved PDF to: {pdf_out_path}")

                else:
                    print(md_content)

            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Conversion failed: {e}")

        if args.url:
            process_url(args.url)

        if args.batch:
            if not os.path.exists(args.batch):
                print(f"Error: Batch file not found: {args.batch}")
                return 1
            with open(args.batch, 'r', encoding='utf-8') as f:
                for line in f:
                    u = line.strip()
                    if u:
                        process_url(u)

        return 0

    ap.print_help()
    return 0
