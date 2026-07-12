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
template.html's three placeholders. YOUTUBE_IDS and AUDIO_IDS are loaded
from data/youtube_map.json and data/audio_map.json (single source of truth)
and re-injected into the template.

Phase 5 adds the service worker / offline media build step: build.py also
copies tools/sw_template.js to sw.js (repo root), injecting the shell cache
version and the enumerated shell asset list, and appends a content-hash
query string (?v={sha256[:8]}) to every audio URL emitted in AUDIO_IDS and
asset-list.json so the two-tier cache (shell-v{N} / media-v1, see plan doc
architecture decision (c)) can address exact file versions.

Emits:
    index.html        - rebuilt page (from template.html)
    sw.js               - service worker (from tools/sw_template.js)
    version.json       - {"version": N, "date": "...", "notes": ""}
    asset-list.json     - {"version": N, "assets": [{url, hash, size}, ...]}
                          for the 32 .ogg files actually referenced by AUDIO_IDS.
                          `url` carries the ?v={hash8} query string; `hash` is
                          the full sha256 for integrity verification.

Usage:
    python build.py [--source-html index.html] [--template template.html]
                     [--xlsx Bhajans.xlsx] [--out index.html]
                     [--version N | --bump] [--notes "..."]

Version handling: by default the version number is carried over unchanged
from the existing version.json (or starts at 1 if none exists). Pass --bump
to increment it by one, or --version N to set it explicitly.
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
# Load YOUTUBE_IDS / AUDIO_IDS from data/ JSON files
# ---------------------------------------------------------------------------

def load_audio_map(audio_map_path):
    """Load AUDIO_IDS from data/audio_map.json.

    This replaces the old verbatim extraction from index.html,
    providing a single source of truth for audio mappings.
    """
    if not audio_map_path.exists():
        raise SystemExit(f"ERROR: {audio_map_path} not found. Run audio pipeline first.")
    with open(audio_map_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_youtube_map(youtube_map_path):
    """Load YOUTUBE_IDS from data/youtube_map.json.

    This replaces the old verbatim extraction from index.html,
    providing a single source of truth for YouTube video mappings.
    """
    if not youtube_map_path.exists():
        raise SystemExit(f"ERROR: {youtube_map_path} not found. Run audio pipeline first.")
    with open(youtube_map_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Asset list + versioned AUDIO_IDS (referenced .ogg files only)
# ---------------------------------------------------------------------------


def compute_audio_assets(audio_ids):
    """De-duplicate + hash the audio files referenced by AUDIO_IDS.

    Returns (versioned_audio_ids, assets):
      versioned_audio_ids: title -> 'audio/x.ogg?v={hash8}' (same set of keys
        as the input audio_ids; the query string lets the service worker and
        the page address an exact file version as a single cache key).
      assets: de-duplicated by underlying path, sorted by path, each entry
        {"url": <versioned url, matches audio_ids values>, "hash": <full
        sha256>, "size": <bytes>} - this is what ships in asset-list.json and
        what DOWNLOAD_ASSETS/PRUNE operate on.
    """
    versioned = {}
    by_path = {}
    for title, path in audio_ids.items():
        full_path = REPO_ROOT / path
        if not full_path.exists():
            print(f"WARNING: audio asset referenced but missing on disk: {path}")
            versioned[title] = path
            continue
        if path not in by_path:
            data = full_path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            by_path[path] = {
                "url": f"{path}?v={digest[:8]}",
                "hash": digest,
                "size": len(data),
            }
        versioned[title] = by_path[path]["url"]
    assets = [by_path[p] for p in sorted(by_path.keys())]
    return versioned, assets


# ---------------------------------------------------------------------------
# Service worker generation (Phase 5)
# ---------------------------------------------------------------------------


def enumerate_shell_assets():
    """Shell precache list: page shell + manifest + icons + self-hosted fonts.

    Deliberately excludes audio/*.ogg (media-v1 territory, never precached)
    and data/asset-list.json/version.json (fetched no-store by the page).
    """
    assets = ["./", "index.html", "manifest.json"]
    icons_dir = REPO_ROOT / "icons"
    if icons_dir.exists():
        for p in sorted(icons_dir.iterdir()):
            if p.is_file():
                assets.append(f"icons/{p.name}")
    fonts_dir = REPO_ROOT / "fonts"
    if fonts_dir.exists():
        for p in sorted(fonts_dir.glob("*.woff2")):
            assets.append(f"fonts/{p.name}")
    return assets


def build_service_worker(version, sw_template_path, out_path):
    template = sw_template_path.read_text(encoding="utf-8")
    shell_assets = enumerate_shell_assets()
    out_text = template.replace("{{SW_VERSION}}", str(version))
    out_text = out_text.replace(
        "{{SHELL_ASSETS}}", json.dumps(shell_assets, ensure_ascii=False)
    )
    out_path.write_text(out_text, encoding="utf-8", newline="")
    return shell_assets


def resolve_version(explicit_version, bump):
    """Version carry-over logic: keep the existing version.json value unless
    --bump (increment by one) or --version N (explicit override) is given."""
    version_path = REPO_ROOT / "version.json"
    existing = 1
    if version_path.exists():
        try:
            existing = int(json.loads(version_path.read_text(encoding="utf-8")).get("version", 1))
        except (json.JSONDecodeError, TypeError, ValueError):
            existing = 1
    if explicit_version is not None:
        return explicit_version
    if bump:
        return existing + 1
    return existing


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build(source_html, template_path, xlsx_path, out_path, version=1, notes=""):
    template_text = template_path.read_text(encoding="utf-8")

    bhajans = load_bhajan_data(xlsx_path)
    youtube_ids = load_youtube_map(REPO_ROOT / "data" / "youtube_map.json")
    audio_ids = load_audio_map(REPO_ROOT / "data" / "audio_map.json")

    versioned_audio_ids, assets = compute_audio_assets(audio_ids)

    bhajans_json = json.dumps(bhajans, ensure_ascii=False)
    youtube_json = json.dumps(youtube_ids, ensure_ascii=False)
    audio_json = json.dumps(versioned_audio_ids, ensure_ascii=False)

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

    asset_list = {"version": version, "assets": assets}
    (REPO_ROOT / "asset-list.json").write_text(
        json.dumps(asset_list, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    shell_assets = build_service_worker(
        version, REPO_ROOT / "tools" / "sw_template.js", REPO_ROOT / "sw.js"
    )

    print(f"Built {out_path}: {len(bhajans)} bhajans, {len(youtube_ids)} youtube ids, "
          f"{len(audio_ids)} audio ids, {len(assets)} referenced media assets.")
    print(f"Built sw.js: version={version}, shell-v{version} ({len(shell_assets)} shell assets), "
          f"media-v1 untouched by build (managed via DOWNLOAD_ASSETS/PRUNE at runtime).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-html", default="index.html",
                     help="deployed HTML to extract YOUTUBE_IDS/AUDIO_IDS from")
    ap.add_argument("--template", default="template.html")
    ap.add_argument("--xlsx", default="Bhajans.xlsx")
    ap.add_argument("--out", default="index.html")
    ap.add_argument("--version", type=int, default=None,
                     help="explicit version override (default: carry over from version.json)")
    ap.add_argument("--bump", action="store_true",
                     help="increment version number by one from the existing version.json")
    ap.add_argument("--notes", default="")
    args = ap.parse_args()

    version = resolve_version(args.version, args.bump)

    build(
        source_html=REPO_ROOT / args.source_html,
        template_path=REPO_ROOT / args.template,
        xlsx_path=REPO_ROOT / args.xlsx,
        out_path=REPO_ROOT / args.out,
        version=version,
        notes=args.notes,
    )


if __name__ == "__main__":
    main()
