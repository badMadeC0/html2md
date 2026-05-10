"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
from urllib.parse import urlparse, unquote
from typing import Any, Callable, Optional


def _load_dependencies() -> tuple[Any, Any]:
    """Load required dynamic dependencies.

    Returns:
        A tuple of (requests, markdownify_md).
    Raises:
        ImportError: If a dependency is missing.
    """
    import requests  # type: ignore  # pylint: disable=import-outside-toplevel
    from markdownify import markdownify as md  # pylint: disable=import-outside-toplevel

    return requests, md


def _setup_session(requests_mod: Any) -> Any:
    """Create and configure a requests session."""
    session = requests_mod.Session()
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


def _process_url(
    target_url: str, session: Any, md: Callable, outdir: Optional[str], requests_mod: Any
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

    request_exception = getattr(requests_mod, "RequestException", Exception)
    if not isinstance(request_exception, type) or not issubclass(
        request_exception, BaseException
    ):
        request_exception = Exception

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
            if not chunk:
                continue
            content_bytes.extend(chunk)
            if len(content_bytes) > max_size:
                print(
                    f"Error: Downloaded content exceeds maximum allowed size ({max_size} bytes).",
                    file=sys.stderr,
                )
                response.close()
                return
        encoding = response.encoding
        if not isinstance(encoding, str) or not encoding:
            encoding = "utf-8"
        content_text = bytes(content_bytes).decode(encoding, errors="replace")

        print("Converting to Markdown...")
        md_content = md(content_text, heading_style="ATX")

        if outdir:
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            # Create a safe filename based on the URL
            filename = "conversion_result.md"
            url_path = target_url.split("?")[0].rstrip("/")
            if url_path:
                base = os.path.basename(unquote(url_path))
                # Sanitize to prevent path traversal
                base = base.replace("/", "_").replace("\\", "_")
                base = base.strip(". ")
                if base:
                    filename = f"{base}.md"

            out_path = os.path.join(outdir, filename)
            # Final safety check: ensure output stays within outdir
            real_outdir = os.path.realpath(outdir)
            real_out_path = os.path.realpath(out_path)
            if os.path.commonpath([real_outdir, real_out_path]) != real_outdir:
                print("Error: Output path escapes output directory.", file=sys.stderr)
                return
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"Success! Saved to: {out_path}")
        else:
            print(md_content)

    except request_exception as e:
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
            requests, md = _load_dependencies()
        except ImportError as e:
            print(
                f"Error: Missing dependency {e.name}."
                "Please run: pip install requests markdownify",
                file=sys.stderr,
            )
            return 1

        session = _setup_session(requests)

        if args.url:
            _process_url(args.url, session, md, args.outdir, requests)

        if args.batch:
            if not os.path.exists(args.batch):
                print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
                return 1
            with open(args.batch, "r", encoding="utf-8") as f:
                for line in f:
                    u = line.strip()
                    if u:
                        _process_url(u, session, md, args.outdir, requests)

        return 0

    ap.print_help()
    return 0
