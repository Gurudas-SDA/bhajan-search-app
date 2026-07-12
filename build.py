#!/usr/bin/env python3
"""
build.py - Rebuilds index.html from template.html + Bhajans.xlsx.

Phase 1 goal: ZERO behavior change vs. the deployed index.html. This script
does not fix any known data bugs (e.g. apostrophe-mismatched AUDIO_IDS keys)
-- byte fidelity with the live page is the target, verified by
tools/verify_roundtrip.py.

Reads Bhajans.xlsx (sheet "Lapa1"; columns Category, Bhajan_Title, Author,
Verse_Number, Original, English, Russian, Latvian, and optionally Spanish,
Italian, French) with pandas, ports the clean_text / clean_latvian_text
logic from generate_html.py, and injects the resulting JSON into
template.html's three placeholders. YOUTUBE_IDS and AUDIO_IDS are extracted
verbatim from the deployed index.html (they get a real data source in a
later phase) and re-injected unchanged.

Emits:
    index.html        - rebuilt page (from template.html)
    version.json       - {"version": N, "date": "...", "notes": ""}
    asset-list.json     - {"version": N, "assets": [{url, hash, size}, ...]}
                          for the 32 MP3s actually referenced by AUDIO_IDS
                          (4 of the 36 files in audio/ are unreferenced and
                          excluded).

Usage:
    python build.py [--source-html index.html] [--template template.html]
                     [--xlsx Bhajans.xlsx] [--out index.html]
"""
import argparse
import hashlib
import json
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Text cleaning (ported verbatim in behavior from generate_html.py)
# ---------------------------------------------------------------------------


def clean_text(text):
    """Clean text fields - remove unwanted symbols (same logic as data_loader.py)."""
    if pd.isna(text):
        return ""
    text = str(text)
    text = text.replace("_x000D_\n", "\n")
    text = text.replace("_x000D_", "\n")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r"\n\s*\n", "\n", text)
    lines = text.split("\n")
    cleaned_lines = [" ".join(line.split()) for line in lines]
    text = "\n".join(cleaned_lines)
    return text.strip()


_latvian_chars = set("ļķģņšžč")
_english_markers = {
    "you", "don", "will", "any", "this", "that", "what", "are",
    "doing", "having", "achieved", "human", "body", "worship",
    "fall", "shameful", "condition", "death", "think", "about",
    "your", "they", "their", "these", "those", "have", "been",
    "would", "could", "should", "which", "when", "where", "rare",
    "son", "now", "into", "time", "does", "not", "worship",
}


def clean_latvian_text(text):
    """Clean Latvian translation field, stripping embedded English lines.

    Excel artefact: some cells contain 'English text\\tLatvian text' on one
    line, or English-only lines inserted between Latvian paragraphs.
    """
    if pd.isna(text):
        return ""
    text = str(text)
    text = text.replace("_x000D_\n", "\n")
    text = text.replace("_x000D_", "\n")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r"\n\s*\n", "\n", text)
    cleaned_lines = []
    for line in text.split("\n"):
        # TAB separator: "English\tLatvian" -> take Latvian part
        if "\t" in line:
            line = line.split("\t")[-1]
        line = " ".join(line.split())
        if not line:
            continue
        # Lines with uniquely Latvian chars -> keep
        if any(c in line for c in _latvian_chars):
            cleaned_lines.append(line)
            continue
        # Long lines with English prose markers -> skip
        words = set(re.findall(r"\b[a-z]+\b", line.lower()))
        if len(words & _english_markers) >= 2 and len(line) > 30:
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


# Extra language columns supported if present in the xlsx (none exist yet;
# must not break when absent).
EXTRA_LANG_COLUMNS = {
    "Spanish": "spanish",
    "Italian": "italian",
    "French": "french",
}


def load_bhajan_data(xlsx_path):
    """Load and process bhajan data from Excel file. Mirrors generate_html.py."""
    df = pd.read_excel(xlsx_path, sheet_name="Lapa1")

    # Clean critical columns, drop rows missing them
    df = df.dropna(subset=["Bhajan_Title", "Author", "Category"])

    base_text_cols = ["Original", "English", "Russian", "Latvian"]
    present_extra_cols = [c for c in EXTRA_LANG_COLUMNS if c in df.columns]

    # Fill missing text fields
    for col in base_text_cols + present_extra_cols:
        df[col] = df[col].fillna("")
    for col in base_text_cols + present_extra_cols:
        if col not in df.columns:
            df[col] = ""

    # Clean all text columns (Latvian gets special cleaner to strip embedded English)
    for col in ["Original", "English", "Russian", "Bhajan_Title", "Author", "Category"] + present_extra_cols:
        df[col] = df[col].apply(clean_text)
    df["Latvian"] = df["Latvian"].apply(clean_latvian_text)

    # Ensure Verse_Number is numeric
    df["Verse_Number"] = pd.to_numeric(df["Verse_Number"], errors="coerce")
    df = df.dropna(subset=["Verse_Number"])
    df["Verse_Number"] = df["Verse_Number"].astype(int)

    # Group by bhajan title
    bhajans = {}
    for _, row in df.iterrows():
        title = row["Bhajan_Title"]
        author = row["Author"]
        category = row["Category"]
        if not title or not author or not category:
            continue
        if title not in bhajans:
            bhajans[title] = {
                "title": title,
                "author": author,
                "category": category,
                "verses": [],
            }
        verse = {
            "number": int(row["Verse_Number"]),
            "original": row["Original"],
            "english": row["English"],
            "russian": row.get("Russian", ""),
            "latvian": row.get("Latvian", ""),
        }
        for col, key in EXTRA_LANG_COLUMNS.items():
            if col in present_extra_cols:
                verse[key] = row.get(col, "")
        bhajans[title]["verses"].append(verse)

    # Sort verses
    for title in bhajans:
        bhajans[title]["verses"].sort(key=lambda x: x["number"])

    result = [b for b in bhajans.values() if b["verses"]]
    return result


# ---------------------------------------------------------------------------
# Extraction of YOUTUBE_IDS / AUDIO_IDS verbatim from a deployed index.html
# ---------------------------------------------------------------------------

_VAR_LINE_RE = {
    "BHAJANS": re.compile(r"^\s*const BHAJANS = (.*);\s*$"),
    "YOUTUBE_IDS": re.compile(r"^\s*const YOUTUBE_IDS = (.*);\s*$"),
    "AUDIO_IDS": re.compile(r"^\s*const AUDIO_IDS = (.*);\s*$"),
}


def extract_js_literal(html_path, varname):
    """Extract and json-parse a `const NAME = <json>;` literal from an HTML file.

    Locates the line by content anchor (line starting with `const NAME = `),
    not by a hard line number.
    """
    prefix = f"const {varname} = "
    with open(html_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith(prefix):
                json_str = stripped[len(prefix):].rstrip(";")
                return json.loads(json_str)
    raise SystemExit(f"ERROR: could not find `const {varname} = ` in {html_path}")


# ---------------------------------------------------------------------------
# Asset list (referenced MP3s only)
# ---------------------------------------------------------------------------


def build_asset_list(audio_ids, audio_dir, version):
    assets = []
    seen = set()
    for title, path in sorted(audio_ids.items()):
        if path in seen:
            continue
        seen.add(path)
        full_path = REPO_ROOT / path
        if not full_path.exists():
            print(f"WARNING: audio asset referenced but missing on disk: {path}")
            continue
        data = full_path.read_bytes()
        assets.append(
            {
                "url": path,
                "hash": hashlib.sha256(data).hexdigest(),
                "size": len(data),
            }
        )
    return {"version": version, "assets": assets}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build(source_html, template_path, xlsx_path, out_path, version=1, notes=""):
    template_text = template_path.read_text(encoding="utf-8")

    bhajans = load_bhajan_data(xlsx_path)
    youtube_ids = extract_js_literal(source_html, "YOUTUBE_IDS")
    audio_ids = extract_js_literal(source_html, "AUDIO_IDS")

    bhajans_json = json.dumps(bhajans, ensure_ascii=False)
    youtube_json = json.dumps(youtube_ids, ensure_ascii=False)
    audio_json = json.dumps(audio_ids, ensure_ascii=False)

    out_text = template_text.replace("{{BHAJANS_JSON}}", bhajans_json, 1)
    out_text = out_text.replace("{{YOUTUBE_IDS_JSON}}", youtube_json, 1)
    out_text = out_text.replace("{{AUDIO_IDS_JSON}}", audio_json, 1)

    out_path.write_text(out_text, encoding="utf-8", newline="")

    version_json = {
        "version": version,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "notes": notes,
    }
    (REPO_ROOT / "version.json").write_text(
        json.dumps(version_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    asset_list = build_asset_list(audio_ids, REPO_ROOT / "audio", version)
    (REPO_ROOT / "asset-list.json").write_text(
        json.dumps(asset_list, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Built {out_path}: {len(bhajans)} bhajans, {len(youtube_ids)} youtube ids, "
          f"{len(audio_ids)} audio ids, {len(asset_list['assets'])} referenced assets.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-html", default="index.html",
                     help="deployed HTML to extract YOUTUBE_IDS/AUDIO_IDS from")
    ap.add_argument("--template", default="template.html")
    ap.add_argument("--xlsx", default="Bhajans.xlsx")
    ap.add_argument("--out", default="index.html")
    ap.add_argument("--version", type=int, default=1)
    ap.add_argument("--notes", default="")
    args = ap.parse_args()

    build(
        source_html=REPO_ROOT / args.source_html,
        template_path=REPO_ROOT / args.template,
        xlsx_path=REPO_ROOT / args.xlsx,
        out_path=REPO_ROOT / args.out,
        version=args.version,
        notes=args.notes,
    )


if __name__ == "__main__":
    main()
