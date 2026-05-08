"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys
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

        def process_url(
            target_url: str, *, emit_output: bool = True
        ) -> tuple[list[str], list[str]]:
            """Process a single URL and optionally return captured output."""
            stdout_messages: list[str] = []
            stderr_messages: list[str] = []

            def write_stdout(message: str) -> None:
                stdout_messages.append(message)
                if emit_output:
                    print(message)

            def write_stderr(message: str) -> None:
                stderr_messages.append(message)
                if emit_output:
                    print(message, file=sys.stderr)

            # Fix common URL typo: trailing slash before query parameters
            if "/?" in target_url:
                target_url = target_url.replace("/?", "?")

            parsed = urlparse(target_url)
            if parsed.scheme not in ("http", "https"):
                write_stderr(
                    f"Error: Unsupported URL scheme '{parsed.scheme}'. "
                    "Only http and https are allowed."
                )
                return stdout_messages, stderr_messages

            write_stdout(f"Processing URL: {target_url}")

            try:
                write_stdout("Fetching content...")
                response = session.get(target_url, timeout=30)
                response.raise_for_status()

                write_stdout("Converting to Markdown...")
                md_content = md(response.text, heading_style="ATX")

                if args.outdir:
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

                    out_path = os.path.join(args.outdir, filename)
                    # Final safety check: ensure output stays within outdir
                    real_outdir = os.path.realpath(args.outdir)
                    real_out_path = os.path.realpath(out_path)
                    if os.path.commonpath([real_outdir, real_out_path]) != real_outdir:
                        write_stderr("Error: Output path escapes output directory.")
                        return stdout_messages, stderr_messages
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(md_content)
                    write_stdout(f"Success! Saved to: {out_path}")
                else:
                    write_stdout(md_content)

            except requests.RequestException as e:
                write_stderr(f"Network error: {e}")
            except OSError as e:
                write_stderr(f"File error: {e}")
            except Exception as e:  # pylint: disable=broad-exception-caught
                write_stderr(f"Conversion failed: {e}")

            return stdout_messages, stderr_messages

        if args.url:
            process_url(args.url)

        if args.batch:
            if not os.path.exists(args.batch):
                print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
                return 1

            if args.outdir:
                os.makedirs(args.outdir, exist_ok=True)

            urls_to_process = []
            with open(args.batch, "r", encoding="utf-8") as f:
                for line in f:
                    u = line.strip()
                    if u:
                        urls_to_process.append(u)

            if urls_to_process:
                from collections import deque  # pylint: disable=import-outside-toplevel
                import concurrent.futures  # pylint: disable=import-outside-toplevel
                from functools import partial  # pylint: disable=import-outside-toplevel

                # Cap max_workers to 10 to avoid overwhelming servers
                max_workers = min(10, len(urls_to_process))
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=max_workers
                ) as executor:
                    if args.outdir:
                        deque(executor.map(process_url, urls_to_process), maxlen=0)
                    else:
                        for stdout_messages, stderr_messages in executor.map(
                            partial(process_url, emit_output=False),
                            urls_to_process,
                        ):
                            for message in stdout_messages:
                                print(message)
                            for message in stderr_messages:
                                print(message, file=sys.stderr)

        return 0

    ap.print_help()
    return 0
