"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
import concurrent.futures
from urllib.parse import urlparse, unquote


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
            from markdownify import (
                markdownify as md,
            )  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            print(
                f"Error: Missing dependency {e.name}."
                "Please run: pip install requests markdownify",
                file=sys.stderr,
            )
            return 1

        session_headers = {
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

        def fetch_url(target_url: str) -> dict:
            """Fetch a single URL and convert to markdown. Thread-safe."""
            if "/?" in target_url:
                target_url = target_url.replace("/?", "?")

            parsed = urlparse(target_url)
            if parsed.scheme not in ("http", "https"):
                return {
                    "url": target_url,
                    "error": f"Error: Unsupported URL scheme '{parsed.scheme}'. Only http and https are allowed.",
                    "type": "scheme",
                }

            try:
                session = requests.Session()
                session.headers.update(session_headers)
                response = session.get(target_url, timeout=30)
                response.raise_for_status()
                md_content = md(response.text, heading_style="ATX")
                return {"url": target_url, "content": md_content, "error": None}
            except requests.RequestException as e:
                return {
                    "url": target_url,
                    "error": f"Network error: {e}",
                    "type": "network",
                }
            except Exception as e:
                return {
                    "url": target_url,
                    "error": f"Conversion failed: {e}",
                    "type": "conversion",
                }
            finally:
                session.close()

        def output_result(result: dict) -> None:
            """Output the result of a single URL sequentially. Not thread-safe."""
            target_url = result["url"]
            print(f"Processing URL: {target_url}")

            if result["error"]:
                print(result["error"], file=sys.stderr)
                return

            print("Fetching content...")
            print("Converting to Markdown...")
            md_content = result["content"]

            if args.outdir:
                if not os.path.exists(args.outdir):
                    try:
                        os.makedirs(args.outdir)
                    except OSError as e:
                        print(f"File error: {e}", file=sys.stderr)
                        return

                filename = "conversion_result.md"
                url_path = target_url.split("?")[0].rstrip("/")
                if url_path:
                    base = os.path.basename(unquote(url_path))
                    base = base.replace("/", "_").replace("\\", "_")
                    base = base.strip(". ")
                    if base:
                        filename = f"{base}.md"

                out_path = os.path.join(args.outdir, filename)
                real_outdir = os.path.realpath(args.outdir)
                real_out_path = os.path.realpath(out_path)
                if os.path.commonpath([real_outdir, real_out_path]) != real_outdir:
                    print(
                        "Error: Output path escapes output directory.", file=sys.stderr
                    )
                    return
                try:
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(md_content)
                    print(f"Success! Saved to: {out_path}")
                except OSError as e:
                    print(f"File error: {e}", file=sys.stderr)
            else:
                print(md_content)

        if args.url:
            result = fetch_url(args.url)
            output_result(result)

        if args.batch:
            if not os.path.exists(args.batch):
                print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
                return 1

            urls_to_process = []
            with open(args.batch, "r", encoding="utf-8") as f:
                for line in f:
                    u = line.strip()
                    if u:
                        urls_to_process.append(u)

            # Process URLs concurrently, but output results sequentially in order
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(fetch_url, urls_to_process)
                for result in results:
                    output_result(result)

        return 0

    ap.print_help()
    return 0
