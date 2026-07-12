#!/usr/bin/env python3
"""One-shot tool: split the deployed index.html into template.html.

Reads index.html, locates the three inline JS literal assignment lines
(BHAJANS, YOUTUBE_IDS, AUDIO_IDS) by robust line-prefix anchors (not hard
line numbers), and replaces each entire line with a placeholder line.
Everything else is copied through byte-for-byte (original line endings are
preserved via newline='' so this works whether the working tree checks out
LF or CRLF).

Usage:
    python tools/split_template.py [index.html] [template.html]
"""
import sys
from pathlib import Path

ANCHORS = [
    ("const BHAJANS = ", "const BHAJANS = {{BHAJANS_JSON}};"),
    ("const YOUTUBE_IDS = ", "const YOUTUBE_IDS = {{YOUTUBE_IDS_JSON}};"),
    ("const AUDIO_IDS = ", "const AUDIO_IDS = {{AUDIO_IDS_JSON}};"),
]


def split_template(src_path: Path, dst_path: Path) -> None:
    with open(src_path, "r", encoding="utf-8", newline="") as f:
        lines = f.readlines()

    # Detect the line ending actually used in this file so the placeholder
    # lines we inject match it exactly (repo may be checked out CRLF or LF).
    newline = "\r\n" if any(l.endswith("\r\n") for l in lines) else "\n"

    remaining_anchors = list(ANCHORS)
    replaced = []
    out_lines = []
    for line in lines:
        stripped = line.lstrip()
        leading_ws = line[: len(line) - len(stripped)]
        matched = None
        for anchor_prefix, placeholder in remaining_anchors:
            if stripped.startswith(anchor_prefix):
                matched = (anchor_prefix, placeholder)
                break
        if matched:
            anchor_prefix, placeholder = matched
            # Preserve this line's exact original indentation instead of
            # assuming a fixed indent -- the deployed file's script block
            # is not uniformly indented.
            out_lines.append(leading_ws + placeholder + newline)
            replaced.append(anchor_prefix)
            remaining_anchors = [a for a in remaining_anchors if a[0] != anchor_prefix]
        else:
            out_lines.append(line)

    if remaining_anchors:
        missing = ", ".join(a[0] for a in remaining_anchors)
        raise SystemExit(
            f"ERROR: could not locate the following anchor line(s) in {src_path}: {missing}"
        )

    with open(dst_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(out_lines)

    print(f"Wrote {dst_path} ({len(out_lines)} lines). Replaced: {', '.join(replaced)}")


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("index.html")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("template.html")
    split_template(src, dst)


if __name__ == "__main__":
    main()
