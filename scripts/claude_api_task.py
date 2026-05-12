"""Use Claude to summarize a sample html2md conversion result."""
from __future__ import annotations

import sys

import anthropic

SAMPLE_HTML = """
<h1>html2md Tool Overview</h1>
<p>The html2md CLI converts HTML pages to Markdown format.</p>
<ul>
  <li>Fetches URLs and converts HTML to Markdown</li>
  <li>Supports batch processing via file input</li>
  <li>Saves output to a configurable output directory</li>
</ul>
<p>It also supports rate limiting, robots.txt controls, and JSONL logging.</p>
"""


def convert_html(html: str) -> str:
    try:
        from markdownify import markdownify as md  # type: ignore
    except ImportError:
        print("Error: markdownify not installed. Run: pip install markdownify", file=sys.stderr)
        sys.exit(1)
    return md(html, heading_style="ATX")


def main() -> int:
    markdown_content = convert_html(SAMPLE_HTML)
    print("Converted Markdown:\n")
    print(markdown_content)

    client = anthropic.Anthropic()

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": "You are a helpful assistant that analyzes Markdown documents.",
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    "Summarize the following Markdown content in one sentence:\n\n"
                    + markdown_content
                ),
            }
        ],
    ) as stream:
        print("Claude's summary:\n")
        for text in stream.text_stream:
            print(text, end="", flush=True)
        print()

        final = stream.get_final_message()
        usage = final.usage
        print(
            f"\n[tokens: input={usage.input_tokens} output={usage.output_tokens}"
            f" cache_read={getattr(usage, 'cache_read_input_tokens', 0)}]"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
