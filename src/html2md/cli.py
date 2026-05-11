"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
from urllib.parse import urlparse, unquote

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

        def decode_response_content(response, content_bytes: bytearray) -> str:
            """Decode streamed bytes without reading consumed response content."""
            encoding = response.encoding
            if not isinstance(encoding, str) or not encoding:
                encoding = 'utf-8'
            bytes_ = bytes(content_bytes)
            try:
                return bytes_.decode(encoding, errors='replace')
            except LookupError:
                return bytes_.decode('utf-8', errors='replace')

        def process_url(target_url: str) -> bool:
            """Process a single URL. Return True when conversion succeeds."""
            # Fix common URL typo: trailing slash before query parameters
            if '/?' in target_url:
                target_url = target_url.replace('/?', '?')

            parsed = urlparse(target_url)
            if parsed.scheme not in ('http', 'https'):
                print(f"Error: Unsupported URL scheme '{parsed.scheme}'. "
                      "Only http and https are allowed.", file=sys.stderr)
                return False

            print(f"Processing URL: {target_url}")

            try:
                print("Fetching content...")
                # Stream response to prevent memory exhaustion DoS. Use a context
                # manager so the connection is released even on errors/early returns.
                with session.get(target_url, timeout=30, stream=True) as response:
                    response.raise_for_status()

                    content_bytes = bytearray()
                    max_size = 10 * 1024 * 1024  # 10 MB limit
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            if len(content_bytes) + len(chunk) > max_size:
                                print(
                                    "Error: Response too large (>10MB). "
                                    "Skipping to prevent memory exhaustion.",
                                    file=sys.stderr,
                                )
                                return False
                            content_bytes.extend(chunk)

                    text_content = decode_response_content(response, content_bytes)

                print("Converting to Markdown...")
                md_content = md(text_content, heading_style="ATX")

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
                        return False
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    print(f"Success! Saved to: {out_path}")
                else:
                    print(md_content)

                return True

            except requests.RequestException as e:
                print(f"Network error: {e}", file=sys.stderr)
            except OSError as e:
                print(f"File error: {e}", file=sys.stderr)
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Conversion failed: {e}", file=sys.stderr)
            return False

        exit_code = 0
        if args.url and not process_url(args.url):
            exit_code = 1

        if args.batch:
            if not os.path.exists(args.batch):
                print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
                return 1
            with open(args.batch, 'r', encoding='utf-8') as f:
                for line in f:
                    u = line.strip()
                    if u and not process_url(u):
                        exit_code = 1

        return exit_code

    ap.print_help()
    return 0
