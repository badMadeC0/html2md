"""Upload utility for html2md."""
from __future__ import annotations

import argparse
import mimetypes
import sys
from pathlib import Path
from typing import Any, Optional

import anthropic


def upload_file(
    file_path: str, client: Optional[anthropic.Anthropic] = None
) -> Any:
    """Upload a file to the Anthropic API.

    Args:
        file_path: Path to the file to upload.
        client: Optional Anthropic client instance to reuse.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    if client is None:
        client = anthropic.Anthropic()

    with path.open("rb") as file_data:
        result = client.beta.files.upload(
            file=(path.name, file_data, mime_type),
        )
    return result


def main(argv=None):
    """Run the upload CLI."""
    ap = argparse.ArgumentParser(
        prog="html2md-upload",
        description="Upload a file to the Anthropic API.",
    )
    ap.add_argument("file", help="Path to the file to upload")
    args = ap.parse_args(argv)

    try:
        # Create client once and pass it, demonstrating reuse pattern
        client = anthropic.Anthropic()
        result = upload_file(args.file, client=client)
        print(f"File uploaded successfully. ID: {result.id}")
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except anthropic.APIError as exc:
        print(f"API error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
