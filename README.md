# Śrī Gauḍīya Gīti-guccha — Bhajan Songbook PWA

## KĀPĒC (Why this exists)

A single self-contained web app that lets devotees browse, search, read and
*listen to* the full bhajan songbook — completely offline once installed.
No backend, no database server, no network dependency at runtime: everything
(259 bhajans, their translations, YouTube references, and 32 recorded
melodies) is baked into one static HTML file plus a service worker that
caches it, and the audio, for offline use.

## KAS (What it is)

- **259 bhajans**, each with per-verse text in up to **6 languages**:
  Original (Sanskrit/Bengali, IAST), English, Russian, Latvian, Spanish,
  Italian, French.
- **52 YouTube references** (linked recordings for bhajans that have one).
- **32 audio recordings** (Opus, 32 kbps mono) playable in-app and
  downloadable for offline listening.
- **Progressive Web App**: installable, works fully offline (shell + on-
  demand audio caching via a service worker), has a manifest + icons.
- **Client-side search** across titles/authors/verse text, font-size
  control, language switcher with shareable per-language URLs.
- No server-side code, no build step at runtime — `index.html` is the
  entire application. Python is only used offline to *generate*
  `index.html` from source data.

## KĀ (How it's built — architecture & data flow)

```
Bhajans.xlsx  ─┐
data/youtube_map.json ─┤
data/audio_map.json ───┼──►  build.py  ──►  index.html  (self-contained app)
template.html ─┘                       ├──►  sw.js          (service worker)
audio/*.ogg  ───────────────────────────┤   ├──►  version.json
                                         │   └──►  asset-list.json
tools/sw_template.js ────────────────────┘
```

- **`Bhajans.xlsx`** (sheet `Lapa1`) is the single source of truth for
  bhajan text: columns `Category, Bhajan_Title, Author, Verse_Number,
  Original, English, Russian, Latvian, Spanish, Italian, French`.
- **`data/youtube_map.json`** and **`data/audio_map.json`** are the single
  source of truth for `YOUTUBE_IDS` and `AUDIO_IDS` (title → YouTube ID /
  audio filename mappings).
- **`template.html`** is `index.html` with three placeholders
  (`BHAJANS`, `YOUTUBE_IDS`, `AUDIO_IDS`) plus all app shell markup, CSS
  and JS (UI strings, search, PWA registration, etc.).
- **`build.py`** reads the xlsx + JSON maps, ports the same text-cleaning
  logic that `generate_html.py` used to use (`clean_text` /
  `clean_latvian_text`), injects the three JSON literals into
  `template.html`, and writes `index.html`. It also:
  - copies `tools/sw_template.js` → `sw.js`, injecting the shell cache
    version and enumerated shell asset list (two-tier cache: `shell-vN`
    for the app shell, `media-v1` for on-demand-downloaded audio, managed
    at runtime rather than rebuilt every version bump);
  - appends a content-hash query string (`?v=<sha256[:8]>`) to every audio
    URL in `AUDIO_IDS` and in `asset-list.json`, so the service worker can
    detect exactly which audio files changed between versions;
  - writes `version.json` (`{version, date, notes}`) and
    `asset-list.json` (list of the 32 referenced `.ogg` assets with
    hash + size), consumed by the app's update-banner / cache-pruning
    logic.
- **`tools/verify_roundtrip.py`** is the correctness gate: it deep-compares
  the `BHAJANS` / `YOUTUBE_IDS` / `AUDIO_IDS` literals of a freshly built
  `index.html` against a reference file (and, with `--xlsx`, against the
  xlsx directly), and diffs everything outside those literals for byte
  identity. Use it whenever you touch `build.py`, `template.html`, or the
  xlsx to make sure nothing regressed.
- **`tools/merge_translations.py`** / **`tools/validate_translations.py`**
  were the one-off tools used to add and QA the Spanish/Italian/French
  columns in `Bhajans.xlsx`; **`tools/split_template.py`** was the one-off
  tool used to derive `template.html` from the original deployed
  `index.html`. All three are dev utilities, not part of the regular
  build.

### Deprecated (kept for reference only)

- **`generate_html.py`** — the old script that hand-generated the deployed
  `index.html` directly from the xlsx (pre-PWA, no service worker, no
  extra languages). Superseded by `build.py` + `template.html`.
- **`match_youtube.py`** — the old one-off script used to populate YouTube
  IDs before `data/youtube_map.json` existed as the source of truth.

Both are left in the repo for historical reference; do not run them as
part of the current build.

## KUR (Where things live / how to update content)

### Update bhajan text or translations

1. Edit `Bhajans.xlsx` (columns as listed above).
2. Rebuild and bump the version:
   ```bash
   python build.py --bump
   ```
   (Omit `--bump` if you want to rebuild without changing the version —
   e.g. after only editing unrelated files.)
3. Sanity-check the rebuild:
   ```bash
   python tools/verify_roundtrip.py --built index.html --reference index.html --xlsx Bhajans.xlsx
   ```
   (or diff against the previous committed `index.html` as the
   `--reference` to see exactly what changed).
4. Commit `index.html`, `sw.js`, `version.json`, `asset-list.json` together
   with the `Bhajans.xlsx` change, then push. The app's built-in update
   banner picks up the new `version.json` for installed/offline users.

### Add or replace audio

- Recordings live in `audio/*.ogg` — **Opus, 32 kbps, mono, 44.1 kHz**
  (chosen to minimize offline storage footprint on phones). Original
  higher-bitrate/MP3 sources are not kept in the working tree; they remain
  recoverable from git history (see the "audio: dedup ... and convert to
  Opus" commit).
- Register a new file in `data/audio_map.json` (`"Bhajan Title":
  "audio/filename.ogg"`), then run `python build.py --bump` — it will
  compute the content hash, append `?v=<hash>` automatically, and add the
  file to `asset-list.json`.

### Add or change a YouTube link

- Edit `data/youtube_map.json` (`"Bhajan Title": "youtube_id"`), then
  rebuild.

### Files at a glance

| Path | Role |
|---|---|
| `index.html` | Built app — the deployable artifact |
| `sw.js` | Built service worker — the deployable artifact |
| `version.json`, `asset-list.json` | Built metadata — deployable artifacts |
| `template.html` | Hand-maintained app shell (HTML/CSS/JS) + placeholders |
| `Bhajans.xlsx` | Hand-maintained bhajan text/translations |
| `data/youtube_map.json`, `data/audio_map.json` | Hand-maintained ID maps |
| `audio/*.ogg` | Hand-maintained audio assets |
| `icons/`, `manifest.json` | PWA install assets |
| `fonts/` | Self-hosted Google Fonts (no runtime CDN dependency) |
| `build.py` | Generator — run this after any content change |
| `tools/verify_roundtrip.py` | Regression gate for the generator |
| `tools/sw_template.js` | Service worker template consumed by `build.py` |

---

## Streamlit version (legacy, local-only)

Before the PWA, this repo also contained a small Streamlit app
(`bhajan_streamlit_app.py` + `data_loader.py`) for browsing the same
`Bhajans.xlsx` locally. It is unrelated to the PWA build above and is kept
only for local/offline dev convenience — it is not deployed.

```bash
pip install -r requirements.txt
streamlit run bhajan_streamlit_app.py
```

It reads `Bhajans.xlsx` from the repo root and opens at
`http://localhost:8501`. See `bhajan_streamlit_app.py` / `data_loader.py`
for details; no further maintenance is planned for this path.

**Hare Kṛṣṇa!**
