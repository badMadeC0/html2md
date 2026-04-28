"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
from pathlib import Path
import sys
from urllib.parse import urlparse, unquote


def _load_dependencies():
    """Load required dependencies."""
    try:
        import requests  # type: ignore  # pylint: disable=import-outside-toplevel

        # pylint: disable=import-outside-toplevel
        from markdownify import (
            markdownify as md,
        )  # pylint: disable=import-outside-toplevel

        return requests, md
    except ImportError as e:
        print(
            f"Error: Missing dependency {e.name}."
            "Please run: pip install requests markdownify",
            file=sys.stderr,
        )
        return None, None


def _setup_session(requests_module):
    """Configure and return a requests Session."""
    session = requests_module.Session()
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
    return session


def _save_to_file(target_url: str, outdir: str, md_content: str) -> None:
    """Save markdown content to a file in the output directory."""
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    # Create a safe filename based on the URL
    filename = "conversion_result.md"
    url_path = target_url.split("?")[0].rstrip("/")
    if url_path:
        base = unquote(url_path).split("/")[-1]
        # Sanitize to prevent path traversal
        base = base.replace("/", "_").replace("\\", "_")
        base = base.strip(". ")
        if base:
            filename = f"{base}.md"

    out_path = outdir_path / filename
    # Final safety check: ensure output stays within outdir
    real_outdir = outdir_path.resolve()
    real_out_path = out_path.resolve()
    try:
        real_out_path.relative_to(real_outdir)
    except ValueError:
        print("Error: Output path escapes output directory.", file=sys.stderr)
        return

    with out_path.open("w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Success! Saved to: {out_path}")


def _process_url(
    target_url: str, outdir: str | None, session, requests_module, md_func
) -> None:
    """Process a single URL."""
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
        response = session.get(target_url, timeout=30)
        response.raise_for_status()

        print("Converting to Markdown...")
        md_content = md_func(response.text, heading_style="ATX")

        if outdir:
            _save_to_file(target_url, outdir, md_content)
        else:
            print(md_content)

    except requests_module.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
    except OSError as e:
        print(f"File error: {e}", file=sys.stderr)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Conversion failed: {e}", file=sys.stderr)


def _process_batch(
    batch_file: str, outdir: str | None, session, requests_module, md_func
) -> int:
    """Process a batch of URLs from a file."""
    if not Path(batch_file).exists():
        print(f"Error: Batch file not found: {batch_file}", file=sys.stderr)
        return 1
    with Path(batch_file).open("r", encoding="utf-8") as f:
        for line in f:
            u = line.strip()
            if u:
                _process_url(u, outdir, session, requests_module, md_func)
    return 0


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
        requests_module, md_func = _load_dependencies()
        if requests_module is None or md_func is None:
            return 1

        session = _setup_session(requests_module)

        if args.url:
            _process_url(args.url, args.outdir, session, requests_module, md_func)

        if args.batch:
            return _process_batch(
                args.batch, args.outdir, session, requests_module, md_func
            )

        return 0

    ap.print_help()
    return 0
