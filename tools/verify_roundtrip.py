#!/usr/bin/env python3
"""
verify_roundtrip.py - THE GATE for Phase 1 (generator rebuild).

Compares a rebuilt index.html against a deployed/reference index.html
(default: the version at git HEAD, or a path you pass explicitly):

1. Parses BHAJANS out of both files and asserts deep equality. Every
   difference is reported with bhajan title + verse number coordinates.
2. Asserts everything OUTSIDE the three JSON blobs (BHAJANS, YOUTUBE_IDS,
   AUDIO_IDS) is byte-identical between the two files (line endings are
   normalized before compare since the working tree may check out CRLF via
   core.autocrlf while git stores LF).
3. If verse content differs between Bhajans.xlsx and the deployed HTML
   (i.e. the deployed HTML has hand-edits not reflected in the xlsx), those
   diffs are reported separately as a proposed xlsx back-port list. The
   deployed HTML is treated as ground truth; Bhajans.xlsx is NEVER modified
   by this script.

Exit code 0 = gate passed (index.html round-trips exactly, or only the
xlsx<->HTML content-diff list is non-empty, which is reported as a warning
not a failure of the generator itself -- see --strict).

Usage:
    python tools/verify_roundtrip.py --built index.html.rebuilt \
        --reference index.html [--xlsx Bhajans.xlsx] [--strict]
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

VARNAMES = ["BHAJANS", "YOUTUBE_IDS", "AUDIO_IDS"]


def extract_literals(html_path):
    """Return dict {varname: (parsed_json, line_index)} plus the raw lines list."""
    with open(html_path, "r", encoding="utf-8", newline="") as f:
        lines = f.readlines()

    literals = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        for varname in VARNAMES:
            prefix = f"const {varname} = "
            if stripped.startswith(prefix):
                json_str = stripped[len(prefix):].rstrip(";")
                literals[varname] = (json.loads(json_str), i)
    missing = [v for v in VARNAMES if v not in literals]
    if missing:
        raise SystemExit(f"ERROR: {html_path} missing literal(s): {', '.join(missing)}")
    return literals, lines


def lines_outside_literals(lines, literal_line_indices):
    """Return the file's lines with the literal lines blanked to a placeholder marker,
    for byte-identity comparison of everything else."""
    out = []
    for i, line in enumerate(lines):
        if i in literal_line_indices:
            out.append(f"__LITERAL_LINE_{i}__\n")
        else:
            out.append(line.replace("\r\n", "\n") if line.endswith("\r\n") else line)
    return out


def deep_diff_bhajans(built, reference, path=""):
    """Yield human-readable diff descriptions between two BHAJANS structures."""
    diffs = []
    if isinstance(reference, list) and isinstance(built, list):
        if len(reference) != len(built):
            diffs.append(f"{path}: length differs (built={len(built)}, reference={len(reference)})")
        # Index by title for list-of-bhajan-dict comparisons, else positional
        if path == "" or path.endswith(".verses"):
            if path == "":
                # top-level: list of bhajan dicts, key by title
                ref_by_title = {b.get("title"): b for b in reference}
                built_by_title = {b.get("title"): b for b in built}
                ref_titles = list(ref_by_title.keys())
                built_titles = list(built_by_title.keys())
                if ref_titles != built_titles:
                    only_ref = [t for t in ref_titles if t not in built_by_title]
                    only_built = [t for t in built_titles if t not in ref_by_title]
                    if only_ref:
                        diffs.append(f"{path}: titles only in reference: {only_ref}")
                    if only_built:
                        diffs.append(f"{path}: titles only in built: {only_built}")
                    if not only_ref and not only_built:
                        diffs.append(f"{path}: bhajan order differs (same set, different order)")
                for title in ref_titles:
                    if title in built_by_title:
                        diffs.extend(deep_diff_bhajans(built_by_title[title], ref_by_title[title], f"[{title}]"))
            else:
                # verses list: key by verse number
                ref_by_num = {v.get("number"): v for v in reference}
                built_by_num = {v.get("number"): v for v in built}
                ref_nums = sorted(ref_by_num.keys())
                built_nums = sorted(built_by_num.keys())
                if ref_nums != built_nums:
                    diffs.append(f"{path}: verse numbers differ (built={built_nums}, reference={ref_nums})")
                for num in ref_nums:
                    if num in built_by_num:
                        diffs.extend(deep_diff_bhajans(built_by_num[num], ref_by_num[num], f"{path}[v{num}]"))
        else:
            for idx, (b_item, r_item) in enumerate(zip(built, reference)):
                diffs.extend(deep_diff_bhajans(b_item, r_item, f"{path}[{idx}]"))
    elif isinstance(reference, dict) and isinstance(built, dict):
        ref_keys = list(reference.keys())
        built_keys = list(built.keys())
        if set(ref_keys) != set(built_keys):
            diffs.append(f"{path}: keys differ (built={built_keys}, reference={ref_keys})")
        for key in ref_keys:
            if key in built:
                child_path = f"{path}.{key}" if not path.endswith("]") else f"{path}.{key}"
                diffs.extend(deep_diff_bhajans(built[key], reference[key], child_path))
    else:
        if built != reference:
            b_repr = repr(built)[:120]
            r_repr = repr(reference)[:120]
            diffs.append(f"{path}: built={b_repr!r} != reference={r_repr!r}")
    return diffs


def diff_xlsx_vs_html(xlsx_path, reference_bhajans):
    """Compare xlsx-derived BHAJANS (post clean_text) against the reference HTML's
    BHAJANS to find hand-edits present only in the deployed HTML."""
    sys.path.insert(0, str(REPO_ROOT))
    import build as build_mod  # local import to avoid hard dependency if unused

    xlsx_bhajans = build_mod.load_bhajan_data(xlsx_path)
    return deep_diff_bhajans(xlsx_bhajans, reference_bhajans)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--built", required=True, help="freshly rebuilt HTML file")
    ap.add_argument("--reference", required=True, help="ground-truth deployed HTML file")
    ap.add_argument("--xlsx", default=None, help="also diff xlsx-derived data against reference HTML")
    ap.add_argument("--strict", action="store_true",
                     help="treat any xlsx<->HTML content diff as a gate failure too")
    args = ap.parse_args()

    built_path = REPO_ROOT / args.built
    ref_path = REPO_ROOT / args.reference

    built_literals, built_lines = extract_literals(built_path)
    ref_literals, ref_lines = extract_literals(ref_path)

    ok = True

    # 1. Deep-equality of the three literals
    for varname in VARNAMES:
        built_val, _ = built_literals[varname]
        ref_val, _ = ref_literals[varname]
        if varname == "BHAJANS":
            diffs = deep_diff_bhajans(built_val, ref_val)
        else:
            diffs = [] if built_val == ref_val else [f"{varname}: dict differs"]
            if diffs:
                # more granular dict diff
                diffs = []
                ref_keys = set(ref_val.keys())
                built_keys = set(built_val.keys())
                for k in sorted(ref_keys - built_keys):
                    diffs.append(f"{varname}[{k!r}]: only in reference")
                for k in sorted(built_keys - ref_keys):
                    diffs.append(f"{varname}[{k!r}]: only in built")
                for k in sorted(ref_keys & built_keys):
                    if ref_val[k] != built_val[k]:
                        diffs.append(f"{varname}[{k!r}]: built={built_val[k]!r} != reference={ref_val[k]!r}")

        if diffs:
            ok = False
            print(f"=== {varname}: {len(diffs)} difference(s) ===")
            for d in diffs[:200]:
                print(" -", d)
            if len(diffs) > 200:
                print(f"   ... and {len(diffs) - 200} more")
        else:
            print(f"OK  {varname}: deep-equal ({len(ref_val) if isinstance(ref_val, (list, dict)) else '-'} entries)")

    # 2. Byte-identity outside the literal lines
    built_literal_idx = {idx for _, idx in built_literals.values()}
    ref_literal_idx = {idx for _, idx in ref_literals.values()}
    built_outside = lines_outside_literals(built_lines, built_literal_idx)
    ref_outside = lines_outside_literals(ref_lines, ref_literal_idx)

    if built_outside != ref_outside:
        ok = False
        print("=== Byte-identity outside literals: FAILED ===")
        import difflib
        diff = list(difflib.unified_diff(ref_outside, built_outside,
                                          fromfile="reference", tofile="built", n=1))
        for line in diff[:200]:
            print(line, end="" if line.endswith("\n") else "\n")
    else:
        print(f"OK  Byte-identity outside literals ({len(ref_outside)} lines)")

    # 3. Optional xlsx<->HTML content diff report (does not fail the gate unless --strict)
    if args.xlsx:
        xlsx_path = REPO_ROOT / args.xlsx
        ref_bhajans, _ = ref_literals["BHAJANS"]
        xlsx_diffs = diff_xlsx_vs_html(xlsx_path, ref_bhajans)
        if xlsx_diffs:
            print(f"=== xlsx <-> deployed HTML content diffs: {len(xlsx_diffs)} " +
                  ("(GATE FAILURE, --strict)" if args.strict else "(informational, not a gate failure)") + " ===")
            for d in xlsx_diffs[:200]:
                print(" -", d)
            if len(xlsx_diffs) > 200:
                print(f"   ... and {len(xlsx_diffs) - 200} more")
            if args.strict:
                ok = False
        else:
            print("OK  xlsx matches deployed HTML content exactly")

    print()
    if ok:
        print("GATE PASSED")
        sys.exit(0)
    else:
        print("GATE FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
