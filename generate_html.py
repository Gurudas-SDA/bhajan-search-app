#!/usr/bin/env python3
"""
generate_html.py - Generates a self-contained index.html from Bhajans.xlsx

Reads the Excel file, groups data by bhajan title, and produces a single-page
application (SPA) with hash-based routing, sticky navigation, and language selector.
"""

import pandas as pd
import json
import re
import unicodedata
from pathlib import Path


def clean_text(text):
    """Clean text fields - remove unwanted symbols (same logic as data_loader.py)."""
    if pd.isna(text):
        return ''
    text = str(text)
    text = text.replace('_x000D_\n', '\n')
    text = text.replace('_x000D_', '\n')
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    text = re.sub(r'\n\s*\n', '\n', text)
    lines = text.split('\n')
    cleaned_lines = [' '.join(line.split()) for line in lines]
    text = '\n'.join(cleaned_lines)
    return text.strip()


_latvian_chars = set('ļķģņšžč')
_english_markers = {
    'you', 'don', 'will', 'any', 'this', 'that', 'what', 'are',
    'doing', 'having', 'achieved', 'human', 'body', 'worship',
    'fall', 'shameful', 'condition', 'death', 'think', 'about',
    'your', 'they', 'their', 'these', 'those', 'have', 'been',
    'would', 'could', 'should', 'which', 'when', 'where', 'rare',
    'son', 'now', 'into', 'time', 'does', 'not', 'worship'
}


def clean_latvian_text(text):
    """Clean Latvian translation field, stripping embedded English lines.

    Excel artefact: some cells contain 'English text\\tLatvian text' on one
    line, or English-only lines inserted between Latvian paragraphs.
    """
    if pd.isna(text):
        return ''
    text = str(text)
    text = text.replace('_x000D_\n', '\n')
    text = text.replace('_x000D_', '\n')
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    text = re.sub(r'\n\s*\n', '\n', text)
    cleaned_lines = []
    for line in text.split('\n'):
        # TAB separator: "English\tLatvian" → take Latvian part
        if '\t' in line:
            line = line.split('\t')[-1]
        line = ' '.join(line.split())
        if not line:
            continue
        # Lines with uniquely Latvian chars → keep
        if any(c in line for c in _latvian_chars):
            cleaned_lines.append(line)
            continue
        # Long lines with English prose markers → skip
        words = set(re.findall(r'\b[a-z]+\b', line.lower()))
        if len(words & _english_markers) >= 2 and len(line) > 30:
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()


def normalize_letter(char):
    """Normalize IAST/Sanskrit first character to ASCII for alphabet grouping."""
    mapping = {
        '\u015a': 'S', '\u015b': 'S',  # Ś ś
        '\u1e62': 'S', '\u1e63': 'S',  # Ṣ ṣ
        '\u1e5a': 'R', '\u1e5b': 'R',  # Ṛ ṛ
        '\u1e44': 'N', '\u1e45': 'N',  # Ṅ ṅ
        '\u00d1': 'N', '\u00f1': 'N',  # Ñ ñ
        '\u1e46': 'N', '\u1e47': 'N',  # Ṇ ṇ
        '\u1e6c': 'T', '\u1e6d': 'T',  # Ṭ ṭ
        '\u1e0c': 'D', '\u1e0d': 'D',  # Ḍ ḍ
        '\u1e40': 'M', '\u1e41': 'M',  # Ṁ ṁ
        '\u1e42': 'M', '\u1e43': 'M',  # Ṃ ṃ
        '\u0100': 'A', '\u0101': 'A',  # Ā ā
        '\u012a': 'I', '\u012b': 'I',  # Ī ī
        '\u016a': 'U', '\u016b': 'U',  # Ū ū
        '\u1e24': 'H', '\u1e25': 'H',  # Ḥ ḥ
        '\u1e36': 'L', '\u1e37': 'L',  # Ḷ ḷ
    }
    if char in mapping:
        return mapping[char]
    # Fallback: NFD decomposition
    decomposed = unicodedata.normalize('NFD', char)
    base = decomposed[0] if decomposed else char
    return base.upper()


def load_bhajan_data(excel_path):
    """Load and process bhajan data from Excel file."""
    df = pd.read_excel(excel_path)

    # Clean critical columns, drop rows missing them
    df = df.dropna(subset=['Bhajan_Title', 'Author', 'Category'])

    # Fill missing text fields
    for col in ['Original', 'English', 'Russian', 'Latvian']:
        if col in df.columns:
            df[col] = df[col].fillna('')
        else:
            df[col] = ''

    # Clean all text columns (Latvian gets special cleaner to strip embedded English)
    for col in ['Original', 'English', 'Russian', 'Bhajan_Title', 'Author', 'Category']:
        df[col] = df[col].apply(clean_text)
    df['Latvian'] = df['Latvian'].apply(clean_latvian_text)

    # Ensure Verse_Number is numeric
    df['Verse_Number'] = pd.to_numeric(df['Verse_Number'], errors='coerce')
    df = df.dropna(subset=['Verse_Number'])
    df['Verse_Number'] = df['Verse_Number'].astype(int)

    # Group by bhajan title
    bhajans = {}
    for _, row in df.iterrows():
        title = row['Bhajan_Title']
        author = row['Author']
        category = row['Category']
        if not title or not author or not category:
            continue
        if title not in bhajans:
            bhajans[title] = {
                'title': title,
                'author': author,
                'category': category,
                'verses': []
            }
        bhajans[title]['verses'].append({
            'number': int(row['Verse_Number']),
            'original': row['Original'],
            'english': row['English'],
            'russian': row.get('Russian', ''),
            'latvian': row.get('Latvian', '')
        })

    # Sort verses
    for title in bhajans:
        bhajans[title]['verses'].sort(key=lambda x: x['number'])

    result = [b for b in bhajans.values() if b['verses']]
    return result


# YouTube video IDs — matched from playlist (newest video wins when duplicates).
# Questionable matches marked with "# ?" — verify before keeping.
YOUTUBE_IDS = {
    "(Kṛṣṇa) Deva! Bhavantaṁ Vande":           "cbHKEN7FVsM",
    "Anūpama Mādhurī Joḓī":                      "sXwq0P0J3jY",
    "Braja-jana-mana-sukhakārī":                  "Oep65u0erDM",
    "Gaurāṅgera Du\u2019ṭī Pada":                "3C0T-aco8x8",
    "Gaurīdāsa-mandire":                          "6eyyNjXFlYA",  # 2019 > 2018
    "Gopīnātha, Mama Nivedana Śunô":             "NJwEUnTExxA",
    "Gāy Gorā Madhura Svare":                    "h4wvw6co094",
    "Hari Bôlbô Āra Madana-mohana Heribô Go":   "MeBH639cbac",
    "Hari Bôle Moder Gaura Elo":                 "4nElJfnMsSY",
    "Hā Hā Mora Gaura-kiśora":                   "E6-vtYptlh8",
    "Jaya Jaya Ballava-rāja-kumāra":             "k89PcScU1C0",  # ? YT: Vallabha-Raja-Kumara
    "Jaya Jaya Harināma":                         "T3M74_5Zbho",
    "Jaya Jaya Jagannātha Śacīra-nandana":       "SYvzUOndM_I",
    "Jaya Jaya Sundara Nanda-kumāra":            "BEn4C0zLttU",
    "Jaya Jaya Śrī Guru":                         "yDqZ4SLZnOU",  # YT: Jaya Jaya Sri Guru, Prema-kalpataru
    "Jaya Rādhā-Mādhava, Jaya Kuñja-bihārī":    "IAtesIV7ZuE",
    "Jhūlā Jhūle Rādhā Dāmodara":               "MT65vbuKULc",
    "Kabe Ha'be Bôlô":                           "zFQevqrFYww",  # YT: Kabe Habe Bolo Se-Dina Amar
    "Kali Kukura":                                "GAQqkvMkUkU",
    "Kalayati Nayanaṁ":                          "ZzRzC0O2wjI",

    "Ke Ĵābi Ke Ĵābi Re Bhāi":                 "IVQpfgw3pWI",
    "Mama Mana Mandire":                          "35RQmHdbd3I",
    "Mādhava, Bahuta Minati Kôri Taya":          "q6nlP04UXOk",
    "Mānasa, Deha, Geha":                        "CTdRROGqGMY",
    "Nitāi Guṇa-maṇi":                           "tPhQRqzH6QA",
    "Nitāi-pada-kamala":                          "yHcWnbQ6oQ0",
    "Pāra Kareṅge":                              "tH8ZWPx7sxs",
    "Ramaṇī-śiromaṇi":                           "GXJv2AXlVgU",
    "Rādhe Jhūlana Padhāro":                     "rb2kE4FQvIE",
    "Rādhe! Jaya Jaya Mādhava-dayite!":          "3Ie2XfVYbW0",
    "Rādhā-Kṛṣṇa Prāṇa Mora":                  "28XrHuo6u6k",
    "Rādhā-kuṇḍa-taṭa":                         "bmfTttLaTfE",
    "Rādhā-nāma Parama Sukhadāī":               "KtCDa6HkeLk",
    "Sakhe, Kalaya Gauram Udāram":               "JK6zIb89BA0",
    "Udilô Aruṇa":                               "LsZy2yG4afw",
    "Śrī Vaiṣṇava-vandanā":                       "--UhvixEIV0",  # YT: Vrindavana Vasi Jata Vaishnavera Gana
    "Vande Viśvambhara":                          "8rlqrH31vQc",
    "Yamunā-puline":                              "qEqfEPaguAI",
    "Yaśomatī-nandana":                          "Mb_NAOC5-cM",
    "Yaṅ Kali Rūpa Śarīra Na Dharata":          "voAXCiJ04y8",
    "Ĵadi Gaurāṅga Nahitô":                     "5WaC96E0zSA",
    "Ĵe Ānilô Prema-dhana":                     "Xg49eKivnPo",
    "Śrī Daśāvatāra-stotram":                   "v5JjODERFLM",
    "Śrī Guru-paramparā":                        "WwJ59AaeqvU",
    "Śrī Gurvāṣṭakam (Bengali Rendition)":      "zyuZRw50XRA",
    "Śrī Kṛṣṇa Caitanya Prabhu Dayā Karô More": "Y0RAubIT6ms",
    "Śrī Kṛṣṇa-virahe":                         "ozEAXCMdcGE",
    "Śrī Maṅgala-gītam":                         "laBce5FeNac",
    "Śrī Nanda-nandanāṣṭakam":                  "9kJfVC0NM10",
    "Śrī Madhurāṣṭakam":                         "9_SZMUako8Q",
    "Śrī Rūpa Mañjarī-pada":                    "Byt3YB5ff80",
    "'Gaurāṅga' Bôlite Ha'be":                  "3pcnUANhye0",
}


def generate_html(bhajans):
    """Generate the complete HTML string."""
    # Compute stats
    total_bhajans = len(bhajans)
    total_verses = sum(len(b['verses']) for b in bhajans)
    categories = sorted(set(b['category'] for b in bhajans))
    authors = sorted(set(b['author'] for b in bhajans))

    bhajans_json = json.dumps(bhajans, ensure_ascii=False)
    youtube_ids_json = json.dumps(YOUTUBE_IDS, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>\u015ar\u012b Gau\u1e0d\u012bya G\u012bti-guccha</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400&family=Noto+Serif:ital,wght@0,400;0,700;1,400&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
  --dark-brown: #4a2c17;
  --saffron: #c86b1f;
  --saffron-dark: #a0541a;
  --saffron-light: #f8e8d4;
  --gold: #b8941f;
  --medium-brown: #6b5340;
  --warm-white: #fdf8f2;
  --light-tan: #f5efe5;
  --border-tan: #e4d5c3;
  --soft-saffron: #fef5eb;
  --text-secondary: #8b7355;
  --maroon: #7a2e2e;
  /* Legacy aliases */
  --orange: var(--saffron);
  --soft-orange: var(--soft-saffron);
}}

html {{ scroll-behavior: smooth; }}

body {{
  font-family: 'Crimson Text', 'Noto Serif', Georgia, serif;
  background: var(--warm-white);
  color: var(--dark-brown);
  line-height: 1.7;
  min-height: 100vh;
}}

/* Breadcrumb */
#breadcrumb {{
  position: sticky;
  top: 0;
  z-index: 100;
  background: linear-gradient(135deg, var(--saffron-dark) 0%, var(--saffron) 100%);
  color: #fff;
  padding: 10px 20px;
  font-family: 'Noto Serif', serif;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(168,84,26,0.25);
}}
#breadcrumb a {{
  color: #fff;
  text-decoration: none;
  opacity: 0.85;
  transition: opacity 0.2s;
}}
#breadcrumb a:hover {{ opacity: 1; text-decoration: underline; }}
#breadcrumb .sep {{ margin: 0 8px; opacity: 0.5; }}
#breadcrumb .current {{ opacity: 1; font-weight: 600; }}

/* Alphabet nav */
#alpha-nav {{
  position: sticky;
  top: 40px;
  z-index: 99;
  background: var(--light-tan);
  border-bottom: 1px solid var(--border-tan);
  padding: 8px 20px;
  text-align: center;
  display: none;
}}
#alpha-nav a {{
  display: inline-block;
  padding: 4px 8px;
  margin: 2px;
  color: var(--medium-brown);
  text-decoration: none;
  font-family: 'Noto Serif', serif;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: 4px;
  transition: all 0.2s;
}}
#alpha-nav a:hover, #alpha-nav a.active {{
  background: var(--orange);
  color: white;
}}
#alpha-nav a.disabled {{
  opacity: 0.3;
  pointer-events: none;
}}

/* Container */
#app {{
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}}

/* Home header */
.home-header {{
  text-align: center;
  padding: 24px 20px 12px;
}}
.home-header h1 {{
  font-family: 'Playfair Display', serif;
  font-size: 2.2rem;
  color: var(--dark-brown);
  margin-bottom: 4px;
  letter-spacing: 1px;
}}
.home-header .subtitle {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem;
  color: var(--medium-brown);
  font-style: italic;
  margin-bottom: 2px;
}}
.home-header .lang-note {{
  font-family: 'Noto Serif', serif;
  font-size: 0.7rem;
  color: var(--text-secondary);
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-top: 4px;
}}

/* Compact header for inner pages */
.compact-header {{
  text-align: center;
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--border-tan);
  margin-bottom: 24px;
}}
.compact-header h1 {{
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem;
  color: var(--dark-brown);
  letter-spacing: 0.5px;
}}
.compact-header h1 span {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 0.95rem;
  color: var(--text-secondary);
  font-style: italic;
  font-weight: 400;
  margin-left: 12px;
}}

/* Decorative divider */
.divider {{
  text-align: center;
  margin: 8px 0;
  color: var(--border-tan);
  font-size: 1rem;
  letter-spacing: 8px;
}}

/* Stats */
.stats {{
  display: flex;
  justify-content: center;
  gap: 32px;
  margin: 8px 0 12px 0;
  flex-wrap: wrap;
}}
.stat {{
  text-align: center;
}}
.stat-number {{
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  color: var(--orange);
  font-weight: 700;
}}
.stat-label {{
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}}

/* Nav buttons — single row */
.nav-grid {{
  display: flex;
  gap: 12px;
  margin: 10px 0;
}}
.nav-btn {{
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 12px;
  background: white;
  border: 1px solid var(--border-tan);
  border-radius: 10px;
  text-decoration: none;
  color: var(--dark-brown);
  text-align: center;
  transition: all 0.3s;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}
.nav-btn:hover {{
  border-color: var(--orange);
  box-shadow: 0 4px 16px rgba(234,88,12,0.12);
  transform: translateY(-2px);
}}
.nav-btn .label {{
  font-family: 'Playfair Display', serif;
  font-size: 1.05rem;
  font-weight: 600;
}}

/* Lists */
.list-section {{
  margin: 20px 0;
}}
.letter-heading {{
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  color: var(--orange);
  border-bottom: 2px solid var(--border-tan);
  padding-bottom: 4px;
  margin: 32px 0 12px;
}}
.bhajan-item {{
  display: block;
  padding: 12px 16px;
  margin: 4px 0;
  background: white;
  border: 1px solid transparent;
  border-radius: 8px;
  text-decoration: none;
  color: var(--dark-brown);
  cursor: pointer;
  transition: all 0.2s;
}}
.bhajan-item:hover {{
  border-color: var(--border-tan);
  background: var(--soft-orange);
}}
.bhajan-item .b-title {{
  font-family: 'Crimson Text', serif;
  font-size: 1.1rem;
  font-weight: 600;
}}
.bhajan-item .b-meta {{
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 2px;
}}
.video-badge {{
  display: inline-block;
  font-size: 0.65rem;
  font-family: var(--font-ui);
  font-weight: 600;
  color: #c0392b;
  background: #fdf0ef;
  border: 1px solid #e8b4b0;
  border-radius: 3px;
  padding: 1px 5px;
  margin-left: 6px;
  vertical-align: middle;
  letter-spacing: 0.03em;
  white-space: nowrap;
}}

/* Category / Author list */
.cat-item {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  margin: 6px 0;
  background: white;
  border: 1px solid var(--border-tan);
  border-radius: 10px;
  text-decoration: none;
  color: var(--dark-brown);
  cursor: pointer;
  transition: all 0.2s;
}}
.cat-item:hover {{
  border-color: var(--orange);
  box-shadow: 0 2px 8px rgba(234,88,12,0.08);
}}
.cat-item .cat-name {{
  font-family: 'Crimson Text', serif;
  font-size: 1.1rem;
  font-weight: 600;
}}
.cat-item .cat-count {{
  background: var(--light-tan);
  color: var(--medium-brown);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}}

/* Bhajan view */
.bhajan-view {{
  padding: 10px 0;
}}
.bhajan-view h2 {{
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem;
  color: var(--dark-brown);
  margin-bottom: 6px;
}}
.bhajan-view .bv-meta {{
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 20px;
}}
.bhajan-view .bv-meta a {{
  color: var(--orange);
  text-decoration: none;
}}
.bhajan-view .bv-meta a:hover {{
  text-decoration: underline;
}}

/* YouTube embed */
.yt-embed {{
  margin: 20px 0;
  border-radius: 10px;
  overflow: hidden;
  aspect-ratio: 16/9;
  background: #000;
  max-width: 560px;
}}
.yt-embed iframe {{
  width: 100%;
  height: 100%;
  display: block;
}}

/* Language selector */
.lang-selector {{
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 20px 0;
}}
.lang-group {{
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}}
.lang-group-dual {{
  border-top: 1px solid var(--border-tan);
  padding-top: 6px;
}}
.lang-btn {{
  padding: 8px 16px;
  border: 1px solid var(--border-tan);
  border-radius: 8px;
  background: white;
  color: var(--medium-brown);
  font-family: 'Noto Serif', serif;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}}
.lang-btn.dual {{
  font-size: 0.78rem;
  padding: 6px 12px;
  color: var(--text-secondary);
  background: var(--cream-light);
}}
.lang-btn:hover {{
  border-color: var(--orange);
}}
.lang-btn.active {{
  background: var(--orange);
  color: white;
  border-color: var(--orange);
}}
/* Dual-language verse display */
.verse-original {{
  font-weight: 600;
  font-style: normal;
  margin-bottom: 10px;
}}
.verse-translation {{
  font-size: 0.88rem;
  color: var(--text-secondary);
  border-left: 2px solid var(--border-tan);
  padding-left: 12px;
  font-style: normal;
}}

/* Verse */
.verse {{
  margin: 24px 0;
  padding: 20px 24px;
  background: white;
  border-left: 3px solid var(--orange);
  border-radius: 0 10px 10px 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}
.verse-number {{
  font-family: 'Playfair Display', serif;
  font-size: 0.8rem;
  color: var(--orange);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
}}
.verse-text {{
  font-family: 'Crimson Text', serif;
  font-size: 1.15rem;
  line-height: 1.9;
  white-space: pre-line;
  color: var(--dark-brown);
}}

/* Page title for list pages */
.page-title {{
  font-family: 'Playfair Display', serif;
  font-size: 1.6rem;
  color: var(--dark-brown);
  margin-bottom: 20px;
}}

/* Footer */
.footer {{
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  font-size: 0.8rem;
  border-top: 1px solid var(--border-tan);
  margin-top: 40px;
}}

/* Responsive */
@media (max-width: 600px) {{
  .home-header h1 {{ font-size: 1.8rem; }}
  .home-header .subtitle {{ font-size: 1rem; }}
  .nav-grid {{ flex-wrap: wrap; }}
  .nav-btn {{ flex: 1 1 45%; }}
  .stats {{ gap: 20px; }}
  .bhajan-view h2 {{ font-size: 1.4rem; }}
  #app {{ padding: 12px; }}
  .verse {{ padding: 14px 16px; }}
  .lang-selector {{ gap: 6px; }}
  .lang-btn {{ padding: 6px 10px; font-size: 0.8rem; }}
  #alpha-nav a {{ padding: 3px 5px; font-size: 0.75rem; }}
  .compact-header h1 {{ font-size: 1.1rem; }}
  .compact-header h1 span {{ display: block; margin-left: 0; margin-top: 2px; }}
}}
</style>
</head>
<body>

<div id="breadcrumb"></div>
<div id="alpha-nav"></div>
<div id="app"></div>

<script>
const BHAJANS = {bhajans_json};

// YouTube video IDs — matched from playlist
const YOUTUBE_IDS = {youtube_ids_json};

// Normalize IAST character to ASCII letter
function normalizeLetter(ch) {{
  const map = {{
    '\\u015a':'S','\\u015b':'S','\\u1e62':'S','\\u1e63':'S',
    '\\u1e5a':'R','\\u1e5b':'R',
    '\\u1e44':'N','\\u1e45':'N','\\u00d1':'N','\\u00f1':'N','\\u1e46':'N','\\u1e47':'N',
    '\\u1e6c':'T','\\u1e6d':'T',
    '\\u1e0c':'D','\\u1e0d':'D',
    '\\u1e40':'M','\\u1e41':'M','\\u1e42':'M','\\u1e43':'M',
    '\\u0100':'A','\\u0101':'A',
    '\\u012a':'I','\\u012b':'I',
    '\\u016a':'U','\\u016b':'U',
    '\\u1e24':'H','\\u1e25':'H',
    '\\u1e36':'L','\\u1e37':'L',
    '\\u014c':'O','\\u014d':'O',
    '\\u0112':'E','\\u0113':'E',
  }};
  if (map[ch]) return map[ch];
  // NFD fallback
  const decomposed = ch.normalize('NFD');
  return decomposed[0].toUpperCase();
}}

function getFirstLetter(text) {{
  if (!text) return '#';
  // Skip leading non-letter characters like (, ), -, spaces
  const cleaned = text.trim().replace(/^[^\\p{{L}}]+/u, '');
  if (!cleaned) return '#';
  return normalizeLetter(cleaned[0]);
}}

// Group bhajans by a key function, returning sorted letter -> bhajans map
function groupByLetter(items, keyFn) {{
  const groups = {{}};
  items.forEach(b => {{
    const letter = getFirstLetter(keyFn(b));
    if (!groups[letter]) groups[letter] = [];
    groups[letter].push(b);
  }});
  // Sort letters
  const sorted = {{}};
  Object.keys(groups).sort().forEach(k => {{
    sorted[k] = groups[k].sort((a, b) => keyFn(a).localeCompare(keyFn(b)));
  }});
  return sorted;
}}

// Escape HTML
function esc(s) {{
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}}

// State
let currentLang = 'original';

// Breadcrumb
function setBreadcrumb(parts) {{
  // parts: [{{"label":"...", "hash":"..."}}, ...]
  const bc = document.getElementById('breadcrumb');
  let html = '<a href="#home" onclick="navigate(\\'home\\')">Home</a>';
  parts.forEach(p => {{
    html += '<span class="sep">\\u203a</span>';
    if (p.hash) {{
      html += '<a href="#' + p.hash + '" onclick="navigate(\\'' + p.hash.replace(/'/g, "\\\\'") + '\\')">' + esc(p.label) + '</a>';
    }} else {{
      html += '<span class="current">' + esc(p.label) + '</span>';
    }}
  }});
  bc.innerHTML = html;
}}

// Alpha nav
function setAlphaNav(letters, scrollPrefix) {{
  const nav = document.getElementById('alpha-nav');
  if (!letters || letters.length === 0) {{
    nav.style.display = 'none';
    return;
  }}
  nav.style.display = 'block';
  const allLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
  const activeSet = new Set(letters);
  let html = '';
  allLetters.forEach(l => {{
    if (activeSet.has(l)) {{
      html += '<a href="#" onclick="scrollToLetter(\\'' + l + '\\', \\'' + scrollPrefix + '\\'); return false;">' + l + '</a>';
    }} else {{
      html += '<a class="disabled">' + l + '</a>';
    }}
  }});
  nav.innerHTML = html;
}}

function scrollToLetter(letter, prefix) {{
  const el = document.getElementById(prefix + '-' + letter);
  if (el) {{
    const bcH = document.getElementById('breadcrumb').offsetHeight;
    const anH = document.getElementById('alpha-nav').offsetHeight;
    const y = el.getBoundingClientRect().top + window.pageYOffset - bcH - anH - 8;
    window.scrollTo({{ top: y, behavior: 'smooth' }});
  }}
}}

// Categories and authors with counts
function getCategoryCounts() {{
  const map = {{}};
  BHAJANS.forEach(b => {{
    map[b.category] = (map[b.category] || 0) + 1;
  }});
  return Object.entries(map).sort((a, b) => a[0].localeCompare(b[0]));
}}

function getAuthorCounts() {{
  const map = {{}};
  BHAJANS.forEach(b => {{
    map[b.author] = (map[b.author] || 0) + 1;
  }});
  return Object.entries(map).sort((a, b) => a[0].localeCompare(b[0]));
}}

// Find bhajan by title
function findBhajan(title) {{
  return BHAJANS.find(b => b.title === title);
}}

// Get verse text by language
function getVerseText(verse, lang) {{
  switch (lang) {{
    case 'english': return verse.english;
    case 'russian': return verse.russian;
    case 'latvian': return verse.latvian;
    default: return verse.original;
  }}
}}

// Check if current mode shows two languages
function isDualLang(lang) {{
  return lang.startsWith('orig+');
}}

// Get translation language from dual mode
function getDualTranslation(verse, lang) {{
  if (lang === 'orig+english') return verse.english;
  if (lang === 'orig+russian') return verse.russian;
  if (lang === 'orig+latvian') return verse.latvian;
  return '';
}}

// Compact header for inner pages
function compactHeader() {{
  return '<div class="compact-header"><h1>\\u015ar\\u012b Gau\\u1e0d\\u012bya G\\u012bti-guccha <span>An Anthology of Gau\\u1e0d\\u012bya Vai\\u1e63\\u1e47ava Songs</span></h1></div>';
}}

// PAGES

function renderHome() {{
  setBreadcrumb([]);
  setAlphaNav(null);
  const catCount = getCategoryCounts().length;
  const authCount = getAuthorCounts().length;
  return `
    <div class="home-header">
      <h1>\\u015ar\\u012b Gau\\u1e0d\\u012bya G\\u012bti-guccha</h1>
      <div class="subtitle">An Anthology of Gau\\u1e0d\\u012bya Vai\\u1e63\\u1e47ava Songs</div>
      <div class="lang-note">In Bengali, Sanskrit, Hindi and Oriya</div>
    </div>
    <div class="divider">\\u2022 \\u2022 \\u2022</div>
    <div class="stats">
      <div class="stat"><div class="stat-number">${{BHAJANS.length}}</div><div class="stat-label">Bhajans</div></div>
      <div class="stat"><div class="stat-number">${{BHAJANS.reduce((s,b)=>s+b.verses.length,0)}}</div><div class="stat-label">Verses</div></div>
      <div class="stat"><div class="stat-number">${{catCount}}</div><div class="stat-label">Categories</div></div>
      <div class="stat"><div class="stat-number">${{authCount}}</div><div class="stat-label">Authors</div></div>
    </div>
    <div class="nav-grid">
      <a class="nav-btn" onclick="navigate('titles')">
        <span class="label">Song Index</span>
      </a>
      <a class="nav-btn" onclick="navigate('firstline')">
        <span class="label">By First Line</span>
      </a>
      <a class="nav-btn" onclick="navigate('categories')">
        <span class="label">By Category</span>
      </a>
      <a class="nav-btn" onclick="navigate('authors')">
        <span class="label">By Author</span>
      </a>
    </div>
    <div class="footer">\\u015ar\\u012b Gau\\u1e0d\\u012bya G\\u012bti-guccha &middot; Devotional Songbook</div>
  `;
}}

function renderTitles() {{
  setBreadcrumb([{{label: 'Song Index', hash: null}}]);
  const groups = groupByLetter(BHAJANS, b => b.title);
  const letters = Object.keys(groups);
  setAlphaNav(letters, 'title');

  let html = compactHeader();
  html += '<div class="list-section">';
  html += '<h2 class="page-title">Song Index</h2>';
  for (const letter of letters) {{
    html += '<div class="letter-heading" id="title-' + letter + '">' + letter + '</div>';
    groups[letter].forEach(b => {{
      const safeTitle = esc(b.title).replace(/'/g, '&#39;');
      html += '<div class="bhajan-item" onclick="navigate(\\'bhajan:\\' + decodeURIComponent(\\'' + encodeURIComponent(b.title) + '\\'))">';
      html += '<div class="b-title">' + esc(b.title) + (YOUTUBE_IDS[b.title] ? ' <span class="video-badge">&#9654; Video</span>' : '') + '</div>';
      html += '<div class="b-meta">' + esc(b.author) + ' &middot; ' + esc(b.category) + ' &middot; ' + b.verses.length + ' verses</div>';
      html += '</div>';
    }});
  }}
  html += '</div>';
  return html;
}}

function renderFirstLine() {{
  setBreadcrumb([{{label: 'By First Line', hash: null}}]);
  // Group by first line of first verse (original)
  const groups = groupByLetter(BHAJANS, b => {{
    if (b.verses.length > 0 && b.verses[0].original) {{
      return b.verses[0].original.split('\\n')[0];
    }}
    return b.title;
  }});
  const letters = Object.keys(groups);
  setAlphaNav(letters, 'fl');

  let html = compactHeader();
  html += '<div class="list-section">';
  html += '<h2 class="page-title">By First Line</h2>';
  for (const letter of letters) {{
    html += '<div class="letter-heading" id="fl-' + letter + '">' + letter + '</div>';
    groups[letter].forEach(b => {{
      const firstLine = (b.verses.length > 0 && b.verses[0].original) ? b.verses[0].original.split('\\n')[0] : b.title;
      html += '<div class="bhajan-item" onclick="navigate(\\'bhajan:\\' + decodeURIComponent(\\'' + encodeURIComponent(b.title) + '\\'))">';
      html += '<div class="b-title">' + esc(firstLine) + (YOUTUBE_IDS[b.title] ? ' <span class="video-badge">&#9654; Video</span>' : '') + '</div>';
      html += '<div class="b-meta">' + esc(b.title) + ' &middot; ' + esc(b.author) + '</div>';
      html += '</div>';
    }});
  }}
  html += '</div>';
  return html;
}}

function renderCategories() {{
  setBreadcrumb([{{label: 'Categories', hash: null}}]);
  setAlphaNav(null);
  const cats = getCategoryCounts();

  let html = compactHeader();
  html += '<h2 class="page-title">Categories</h2>';
  cats.forEach(([name, count]) => {{
    html += '<div class="cat-item" onclick="navigate(\\'category:\\' + decodeURIComponent(\\'' + encodeURIComponent(name) + '\\'))">';
    html += '<span class="cat-name">' + esc(name) + '</span>';
    html += '<span class="cat-count">' + count + '</span>';
    html += '</div>';
  }});
  return html;
}}

function renderAuthors() {{
  setBreadcrumb([{{label: 'Authors', hash: null}}]);
  setAlphaNav(null);
  const auths = getAuthorCounts();

  let html = compactHeader();
  html += '<h2 class="page-title">Authors</h2>';
  auths.forEach(([name, count]) => {{
    html += '<div class="cat-item" onclick="navigate(\\'author:\\' + decodeURIComponent(\\'' + encodeURIComponent(name) + '\\'))">';
    html += '<span class="cat-name">' + esc(name) + '</span>';
    html += '<span class="cat-count">' + count + '</span>';
    html += '</div>';
  }});
  return html;
}}

function renderCategoryView(catName) {{
  setBreadcrumb([
    {{label: 'Categories', hash: 'categories'}},
    {{label: catName, hash: null}}
  ]);
  setAlphaNav(null);
  const items = BHAJANS.filter(b => b.category === catName).sort((a,b) => a.title.localeCompare(b.title));

  let html = compactHeader();
  html += '<h2 class="page-title">' + esc(catName) + '</h2>';
  html += '<p style="color:var(--text-secondary);margin-bottom:16px;">' + items.length + ' bhajans</p>';
  items.forEach(b => {{
    html += '<div class="bhajan-item" onclick="navigate(\\'bhajan:\\' + decodeURIComponent(\\'' + encodeURIComponent(b.title) + '\\'))">';
    html += '<div class="b-title">' + esc(b.title) + (YOUTUBE_IDS[b.title] ? ' <span class="video-badge">&#9654; Video</span>' : '') + '</div>';
    html += '<div class="b-meta">' + esc(b.author) + ' &middot; ' + b.verses.length + ' verses</div>';
    html += '</div>';
  }});
  return html;
}}

function renderAuthorView(authName) {{
  setBreadcrumb([
    {{label: 'Authors', hash: 'authors'}},
    {{label: authName, hash: null}}
  ]);
  setAlphaNav(null);
  const items = BHAJANS.filter(b => b.author === authName).sort((a,b) => a.title.localeCompare(b.title));

  let html = compactHeader();
  html += '<h2 class="page-title">' + esc(authName) + '</h2>';
  html += '<p style="color:var(--text-secondary);margin-bottom:16px;">' + items.length + ' bhajans</p>';
  items.forEach(b => {{
    html += '<div class="bhajan-item" onclick="navigate(\\'bhajan:\\' + decodeURIComponent(\\'' + encodeURIComponent(b.title) + '\\'))">';
    html += '<div class="b-title">' + esc(b.title) + (YOUTUBE_IDS[b.title] ? ' <span class="video-badge">&#9654; Video</span>' : '') + '</div>';
    html += '<div class="b-meta">' + esc(b.category) + ' &middot; ' + b.verses.length + ' verses</div>';
    html += '</div>';
  }});
  return html;
}}

function renderBhajan(title) {{
  const b = findBhajan(title);
  if (!b) return '<p>Bhajan not found.</p>';

  setBreadcrumb([
    {{label: b.category, hash: 'category:' + encodeURIComponent(b.category)}},
    {{label: b.title, hash: null}}
  ]);
  setAlphaNav(null);

  let html = compactHeader();
  html += '<div class="bhajan-view">';
  html += '<h2>' + esc(b.title) + '</h2>';
  html += '<div class="bv-meta">';
  html += 'by <a href="#" onclick="navigate(\\'author:' + encodeURIComponent(b.author) + '\\'); return false;">' + esc(b.author) + '</a>';
  html += ' &middot; <a href="#" onclick="navigate(\\'category:' + encodeURIComponent(b.category) + '\\'); return false;">' + esc(b.category) + '</a>';
  html += ' &middot; ' + b.verses.length + ' verses';
  html += '</div>';

  // YouTube embed (if available)
  const ytId = YOUTUBE_IDS[b.title];
  if (ytId) {{
    html += '<div class="yt-embed">';
    html += '<iframe src="https://www.youtube.com/embed/' + ytId + '?rel=0" frameborder="0" allowfullscreen loading="lazy"></iframe>';
    html += '</div>';
  }}

  // Language selector — single language
  const enc = encodeURIComponent(title);
  html += '<div class="lang-selector">';
  html += '<div class="lang-group">';
  html += '<button class="lang-btn' + (currentLang==='original' ? ' active' : '') + '" onclick="switchLang(\\'original\\',\\'' + enc + '\\')">Original</button>';
  html += '<button class="lang-btn' + (currentLang==='english' ? ' active' : '') + '" onclick="switchLang(\\'english\\',\\'' + enc + '\\')">English</button>';
  html += '<button class="lang-btn' + (currentLang==='latvian' ? ' active' : '') + '" onclick="switchLang(\\'latvian\\',\\'' + enc + '\\')">Latvie\\u0161u</button>';
  html += '<button class="lang-btn' + (currentLang==='russian' ? ' active' : '') + '" onclick="switchLang(\\'russian\\',\\'' + enc + '\\')">\\u0420\\u0443\\u0441\\u0441\\u043a\\u0438\\u0439</button>';
  html += '</div>';
  // Combined language options
  html += '<div class="lang-group lang-group-dual">';
  html += '<button class="lang-btn dual' + (currentLang==='orig+english' ? ' active' : '') + '" onclick="switchLang(\\'orig+english\\',\\'' + enc + '\\')">Original + English</button>';
  html += '<button class="lang-btn dual' + (currentLang==='orig+latvian' ? ' active' : '') + '" onclick="switchLang(\\'orig+latvian\\',\\'' + enc + '\\')">Original + Latvie\\u0161u</button>';
  html += '<button class="lang-btn dual' + (currentLang==='orig+russian' ? ' active' : '') + '" onclick="switchLang(\\'orig+russian\\',\\'' + enc + '\\')">Original + \\u0420\\u0443\\u0441\\u0441\\u043a\\u0438\\u0439</button>';
  html += '</div>';
  html += '</div>';

  // Verses
  b.verses.forEach(v => {{
    html += '<div class="verse">';
    html += '<div class="verse-number">Verse ' + v.number + '</div>';
    if (isDualLang(currentLang)) {{
      const orig = v.original;
      const trans = getDualTranslation(v, currentLang);
      if (orig) html += '<div class="verse-text verse-original">' + esc(orig) + '</div>';
      if (trans) {{
        html += '<div class="verse-text verse-translation">' + esc(trans) + '</div>';
      }} else {{
        html += '<div class="verse-text" style="color:var(--text-secondary);font-style:italic;">Translation not available</div>';
      }}
    }} else {{
      const text = getVerseText(v, currentLang);
      if (text) {{
        html += '<div class="verse-text">' + esc(text) + '</div>';
      }} else {{
        html += '<div class="verse-text" style="color:var(--text-secondary);font-style:italic;">Translation not available</div>';
      }}
    }}
    html += '</div>';
  }});
  html += '</div>';
  return html;
}}

function switchLang(lang, encodedTitle) {{
  currentLang = lang;
  const title = decodeURIComponent(encodedTitle);
  render('bhajan:' + title, true);
}}

// Router
function navigate(route) {{
  window.location.hash = route;
}}

function render(route, preserveScroll) {{
  const app = document.getElementById('app');
  const scrollPos = preserveScroll ? window.pageYOffset : 0;

  if (!route || route === 'home') {{
    app.innerHTML = renderHome();
  }} else if (route === 'titles') {{
    app.innerHTML = renderTitles();
  }} else if (route === 'firstline') {{
    app.innerHTML = renderFirstLine();
  }} else if (route === 'categories') {{
    app.innerHTML = renderCategories();
  }} else if (route === 'authors') {{
    app.innerHTML = renderAuthors();
  }} else if (route.startsWith('category:')) {{
    const name = decodeURIComponent(route.substring(9));
    app.innerHTML = renderCategoryView(name);
  }} else if (route.startsWith('author:')) {{
    const name = decodeURIComponent(route.substring(7));
    app.innerHTML = renderAuthorView(name);
  }} else if (route.startsWith('bhajan:')) {{
    const title = decodeURIComponent(route.substring(7));
    app.innerHTML = renderBhajan(title);
  }} else {{
    app.innerHTML = renderHome();
  }}

  if (preserveScroll) {{
    window.scrollTo(0, scrollPos);
  }} else {{
    window.scrollTo(0, 0);
  }}
}}

// Hash listener
window.addEventListener('hashchange', () => {{
  const route = window.location.hash.substring(1);
  render(route);
}});

// Initial render
const initRoute = window.location.hash.substring(1) || 'home';
render(initRoute);
</script>

</body>
</html>'''
    return html


def main():
    script_dir = Path(__file__).parent
    excel_path = script_dir / 'Bhajans.xlsx'

    if not excel_path.exists():
        print(f"ERROR: {excel_path} not found!")
        return

    print(f"Reading {excel_path}...")
    bhajans = load_bhajan_data(excel_path)

    total_verses = sum(len(b['verses']) for b in bhajans)
    categories = sorted(set(b['category'] for b in bhajans))
    authors = sorted(set(b['author'] for b in bhajans))

    print(f"\nSummary:")
    print(f"  Bhajans:    {len(bhajans)}")
    print(f"  Verses:     {total_verses}")
    print(f"  Categories: {len(categories)}")
    print(f"  Authors:    {len(authors)}")

    print(f"\nCategories: {', '.join(categories)}")
    print(f"\nGenerating HTML...")

    html_content = generate_html(bhajans)

    output_path = script_dir / 'index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    size_kb = output_path.stat().st_size / 1024
    print(f"  Output: {output_path} ({size_kb:.1f} KB)")
    print(f"\nDone! Open index.html in a browser.")


if __name__ == '__main__':
    main()
