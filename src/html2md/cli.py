"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
from pathlib import Path


def main(argv=None):
    """Run the CLI."""
    ap = argparse.ArgumentParser(
        prog="html2md", description="Convert HTML URL to Markdown."
    )
    ap.add_argument("--help-only", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--url", help="Input URL to convert")
    ap.add_argument("--batch", help="File containing URLs to process (one per line)")
    ap.add_argument("--outdir", help="Output directory to save the file")
    ap.add_argument(
        "--all-formats", action="store_true", help="Generate all formats (placeholder)"
    )
    ap.add_argument('--help-only', action='store_true', help=argparse.SUPPRESS)
    ap.add_argument('--url', help='Input URL to convert')
    ap.add_argument('--batch', help='File containing URLs to process (one per line)')
    ap.add_argument('--outdir', help='Output directory to save the file')
    ap.add_argument('--all-formats', action='store_true', help=argparse.SUPPRESS)

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
                "Please run: pip install requests markdownify"
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

            print(f"Processing URL: {target_url}")

            try:
                print("Fetching content...")
                response = session.get(target_url, timeout=30)
                response.raise_for_status()

                print("Converting to Markdown...")
                md_content = md(response.text, heading_style="ATX")

                if args.outdir:
                    os.makedirs(args.outdir, exist_ok=True)

                    # Create a simple filename based on the URL
                    filename = "conversion_result.md"
                    url_path = target_url.split("?")[0].rstrip("/")
                    if url_path:
                        base = os.path.basename(url_path)
                        if base:
                            filename = f"{base}.md"

                    out_path = os.path.join(args.outdir, filename)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(md_content)
                    print(f"Success! Saved to: {out_path}")
                else:
                    print(md_content)

            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Conversion failed: {e}")

        if args.url:
            process_url(args.url)

        if args.batch:
            batch_path = Path(args.batch)
            if not batch_path.exists():
                print(f"Error: Batch file not found: {args.batch}")
                return 1
            with batch_path.open("r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]

            if args.outdir:
                # Use parallel processing when outputting to files
                import concurrent.futures

                # Limit workers to 5 to avoid overwhelming servers
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    list(executor.map(process_url, urls))
            else:
                for u in urls:
                    process_url(u)

        return 0

    ap.print_help()
    return 0
