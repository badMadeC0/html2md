from __future__ import annotations

import argparse
import os


def main(argv=None):
    """Run the CLI."""
    ap = argparse.ArgumentParser(prog="html2md", description="Convert HTML URL to Markdown.")
    ap.add_argument("--help-only", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--url", help="Input URL to convert")
    ap.add_argument("--batch", help="File containing URLs to process (one per line)")
    ap.add_argument("--outdir", help="Output directory to save the file")
    ap.add_argument("--all-formats", action="store_true", help="Generate all formats (placeholder)")

    args = ap.parse_args(argv)

    if args.help_only:
        ap.print_help()
        return 0

    if args.url or args.batch:
        try:
            import requests  # type: ignore  # pylint: disable=import-outside-toplevel
            from markdownify import markdownify as md  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            print(
                f"Error: Missing dependency {e.name}."
                "Please run: pip install requests markdownify"
            )
            return 1

        session = requests.Session()

        def process_url(target_url: str) -> None:
            if "/?" in target_url:
                target_url = target_url.replace('/?', '?')

            print(f"Processing URL: {target_url}")

            try:
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                }
                response = session.get(target_url, headers=headers, timeout=30)
                response.raise_for_status()

                md_content = md(response.text, heading_style="ATX")

                if args.outdir:
                    os.makedirs(args.outdir, exist_ok=True)
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
            if not os.path.exists(args.batch):
                print(f"Error: Batch file not found: {args.batch}")
                return 1
            with open(args.batch, "r", encoding="utf-8") as f:
                for line in f:
                    u = line.strip()
                    if u:
                        process_url(u)

        return 0

    ap.print_help()
    return 0
