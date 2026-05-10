"""CLI entry point for html2md."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse


def process_url(  # pylint: disable=too-many-locals
    target_url: str, session: Any, outdir: Optional[str], md_func: Any
) -> None:
    """Process a single URL."""
    import requests  # pylint: disable=import-outside-toplevel

    # Fix common URL typo: trailing slash before query parameters
    if "/?" in target_url:
        target_url = target_url.replace("/?", "?")

    parsed = urlparse(target_url)
    if parsed.scheme not in ("http", "https"):
        print(
            f"Error: Unsupported URL scheme '{parsed.scheme}'. "
            "Only http and https are allowed.",
            file=sys.stderr,
        )
        return

    print(f"Processing URL: {target_url}")

    try:
        print("Fetching content...")
        # Security: Stream response and enforce 10MB limit to prevent DoS (OOM)
        response = session.get(target_url, timeout=30, stream=True)
        response.raise_for_status()

        max_size = 10 * 1024 * 1024
        try:
            if int(response.headers.get("Content-Length", 0)) > max_size:
                print(
                    f"Error: Content-Length exceeds maximum allowed size ({max_size} bytes).",
                    file=sys.stderr,
                )
                response.close()
                return
        except ValueError:
            # Invalid or non-numeric Content-Length: treat as unknown size.
            # The streaming loop below still enforces max_size.
            pass

        content_bytes = bytearray()
        for chunk in response.iter_content(chunk_size=8192):
            content_bytes.extend(chunk)
            if len(content_bytes) > max_size:
                print(
                    f"Error: Downloaded content exceeds maximum allowed size ({max_size} bytes).",
                    file=sys.stderr,
                )
                response.close()
                return
        response_encoding = response.encoding
        if not isinstance(response_encoding, str) or not response_encoding:
            response_encoding = "utf-8"
        html_text = bytes(content_bytes).decode(response_encoding, errors="replace")

        print("Converting to Markdown...")
        md_content = md_func(html_text, heading_style="ATX")

        if outdir:
            outdir_path = Path(outdir)
            outdir_path.mkdir(parents=True, exist_ok=True)

            # Create a safe filename based on the URL
            filename = "conversion_result.md"
            url_path = unquote(parsed.path).rstrip("/")
            if url_path:
                base = Path(url_path).name
                # Sanitize to prevent path traversal
                base = base.replace("/", "_").replace("\\", "_")
                base = base.strip(". ")
                if base:
                    filename = f"{base}.md"

            out_path = outdir_path / filename
            # Final safety check: ensure output stays within outdir
            real_outdir = outdir_path.resolve(strict=False)
            real_out_path = out_path.resolve(strict=False)
            try:
                real_out_path.relative_to(real_outdir)
            except ValueError:
                print("Error: Output path escapes output directory.", file=sys.stderr)
                return
            with out_path.open("w", encoding="utf-8") as f:
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


def main(argv=None):
    """Run the CLI."""
    ap = argparse.ArgumentParser(
        prog="html2md", description="Convert HTML URL to Markdown."
    )
    ap.add_argument("--help-only", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--url", help="Input URL to convert")
    ap.add_argument("--batch", help="File containing URLs to process (one per line)")
    ap.add_argument("--outdir", help="Output directory to save the file")

    args = ap.parse_args(argv)

    if args.help_only:
        ap.print_help()
        return 0

    if args.url or args.batch:
        try:
            import requests  # type: ignore  # pylint: disable=import-outside-toplevel
            from markdownify import (  # pylint: disable=import-outside-toplevel
                markdownify as md,
            )
        except ImportError as e:
            print(
                f"Error: Missing dependency {e.name}."
                "Please run: pip install requests markdownify",
                file=sys.stderr,
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

        if args.url:
            process_url(args.url, session, args.outdir, md)

        if args.batch:
            batch_path = Path(args.batch)
            if not batch_path.exists():
                print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
                return 1
            with batch_path.open("r", encoding="utf-8") as f:
                for line in f:
                    u = line.strip()
                    if u:
                        process_url(u, session, args.outdir, md)

        return 0

    ap.print_help()
    return 0
