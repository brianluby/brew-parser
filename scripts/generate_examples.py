#!/usr/bin/env python3
"""
Generate example outputs (JSON, Markdown, and Rich table capture) from a sample diff.

Outputs are written under `examples/`:
- changes-example.json
- markdown-example.md
- table-example.txt
- table-example.html
"""

from pathlib import Path
import json
from rich.console import Console
from brew_parser import BrewParser


def build_sample_diff():
    return {
        "added": [
            {
                "name": "ripgrep",
                "desc": "Line-oriented search tool that recursively searches your current directory for a regex pattern",
                "homepage": "https://github.com/BurntSushi/ripgrep",
                "versions": {"stable": "14.1.0"},
            },
            {
                "name": "fd",
                "desc": "Simple, fast and user-friendly alternative to 'find'",
                "homepage": "https://github.com/sharkdp/fd",
                "versions": {"stable": "8.7.0"},
            },
        ],
        "removed": [
            {
                "name": "oldtool",
                "desc": "Deprecated tool",
                "versions": {"stable": "0.9.0"},
            }
        ],
        "updated": [
            {
                "name": "httpie",
                "desc": "User-friendly cURL replacement (command-line HTTP client)",
                "old_version": "3.2.0",
                "new_version": "3.3.0",
            }
        ],
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    outdir = root / "examples"
    outdir.mkdir(exist_ok=True)

    diff = build_sample_diff()

    # JSON payload with summary
    payload = {
        "summary": {
            "added": len(diff["added"]),
            "removed": len(diff["removed"]),
            "updated": len(diff["updated"]),
        },
        **diff,
    }
    (outdir / "changes-example.json").write_text(json.dumps(payload, indent=2) + "\n")

    # Markdown using tool's formatter
    parser = BrewParser()
    md_text = parser.format_diff_as_markdown(diff)
    (outdir / "markdown-example.md").write_text(md_text + "\n")

    # Table capture using Rich (text + HTML)
    parser.console = Console(record=True)
    parser.format_diff_as_table(diff)
    text_capture = parser.console.export_text(clear=False)
    html_capture = parser.console.export_html(clear=False, inline_styles=True)
    (outdir / "table-example.txt").write_text(text_capture)
    (outdir / "table-example.html").write_text(html_capture)


if __name__ == "__main__":
    main()

