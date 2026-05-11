"""CLI entry point for html2md."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


def _build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="html2md",
        description="Convert HTML URL to Markdown.",
    )
    parser.add_argument("--help-only", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--url", help="Input URL to convert")
    parser.add_argument("--batch", help="File containing URLs to process (one per line)")
    parser.add_argument("--outdir", help="Output directory to save the file")
    return parser


def _output_filename(target_url: str) -> str:
    """Return a safe Markdown filename derived from a URL path."""
    parsed = urlparse(target_url)
    base = os.path.basename(unquote(parsed.path.rstrip("/")))
    base = base.replace("/", "_").replace("\\", "_").strip(". ")
    return f"{base}.md" if base else "conversion_result.md"


def _contained_output_path(outdir: str, target_url: str) -> Path | None:
    """Return an output path only when it remains inside outdir.

    Args:
        outdir: Directory requested by the user for generated Markdown.
        target_url: Source URL used to derive the destination filename.

    Returns:
        A contained output path, or ``None`` when the resolved path escapes
        the requested output directory.

    Side Effects:
        Creates ``outdir`` and missing parents when needed.
    """
    output_dir = Path(outdir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / _output_filename(target_url)
    real_outdir = output_dir.resolve()
    real_output_path = output_path.resolve(strict=False)
    if os.path.commonpath([str(real_outdir), str(real_output_path)]) != str(real_outdir):
        return None
    return output_path


def main(argv=None):
    """Run the CLI."""
    ap = _build_parser()
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
                    out_path = _contained_output_path(args.outdir, target_url)
                    if out_path is None:
                        print("Error: Output path escapes output directory.",
                              file=sys.stderr)
                        return
                    with out_path.open('w', encoding='utf-8') as f:
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
            batch_path = Path(args.batch)
            if not batch_path.exists():
                print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
                return 1
            with batch_path.open('r', encoding='utf-8') as f:
                for line in f:
                    u = line.strip()
                    if u:
                        process_url(u)

        return 0

    ap.print_help()
    return 0
