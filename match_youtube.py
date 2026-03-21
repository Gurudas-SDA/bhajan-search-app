#!/usr/bin/env python3
"""
match_youtube.py - Matches YouTube playlist videos to bhajan titles.
Playlist is ordered newest→oldest, so first match wins (newest video kept).
Run: python match_youtube.py
"""

import re
import unicodedata
import pandas as pd
from difflib import SequenceMatcher

# Full playlist scraped from YouTube (newest first)
RAW_PLAYLIST = """ozEAXCMdcGE|||Bhajan Śrī Kṛṣṇa-virahe by Śrīla Bhaktivinoda Ṭhākura - 2025-12-07 - Sri Prem Prayojan
qEqfEPaguAI|||Bhajan Yamunā-puline - 2025-06-01 Sri Prem Prayojan
3C0T-aco8x8|||Bhajan Gaurāṅgera Du'ṭī Pada - 2024-07-21 - Sri Prem Prayojan
SYvzUOndM_I|||Bhajan Jaya Jaya Jagannātha Śacīra-nandana - 2025-02-12 - Sri Prem Prayojan
tH8ZWPx7sxs|||Bhajan Pāra Kareṅge - 2024-08-19 - Sri Prem Prayojan
Byt3YB5ff80|||Bhajan Śrī Rūpa Mañjarī-pada - 2024-08-17 - Sri Prem Prayojan
GXJv2AXlVgU|||Bhajan Ramaṇī-śiromaṇi - 2024-08-16 - Sri Prem Prayojan
yDqZ4SLZnOU|||Bhajan Jaya Jaya Śrī Guru, Prema-kalpataru - 2024-04-23 - Sri Prem Prayojan
3Ie2XfVYbW0|||Bhajan Rādhe! Jaya Jaya Mādhava-dayite! - 2024-04-21 - Sri Prem Prayojan
yHcWnbQ6oQ0|||Bhajan Nitāi-pada-kamala - 2024-06-22 - Sri Prem Prayojan
NJwEUnTExxA|||Bhajan Gopīnātha, Mama Nivedana Śunô - 2024-06-22 - Sri Prem Prayojan
KtCDa6HkeLk|||Bhajan Rādhā-nāma Parama Sukha-dāi - 2024-06-21 - Sri Prem Prayojan
5WaC96E0zSA|||Bhajan Ĵadi Gaurāṅga Nahitô - 2024-06-21 - Sri Prem Prayojan
E6-vtYptlh8|||Bhajan Hā Hā Mora Gaura-Kiśora - 2024-03-24 - Sri Prem Prayojan
KYQvsF1Qo_E|||Sri Nrsimha Pranama - 2024-05-22 - Sri Prem Prayojan
q6nlP04UXOk|||Bhajan Mādhava, Bahuta Minati Kôri Taya - 2024-05-22 - Sri Prem Prayojan
9kJfVC0NM10|||Bhajan Śrī Nanda-nandanāṣṭakam (Namāmi Nanda-nandanam) - 2024-05-22 - Sri Prem Prayojan
T3M74_5Zbho|||Bhajan Jaya Jaya Harināma - 2024-05-23 - Sri Prem Prayojan
3dDFhuKccZU|||Bhajan Yamunā-puline - 2024-03-22 - Sri Prem Prayojan
--UhvixEIV0|||Bhajan Vrindavana Vasi Jata Vaishnavera Gana - 2022-05-28 - Sri Prem Prayojan
WwJ59AaeqvU|||Bhajan Sri Guru-Parampara (Krishna Hoite Chaturmukha) - 2022-05-27 - Sri Prem Prayojan
28XrHuo6u6k|||Bhajan Radha-Krishna Prana Mora - 2023-09-05 - Sri Prem Prayojan
Tj_hv1KVYSo|||Bhajan Savarana Sri Gaura Mahima - 2023-09-05 - Sri Prem Prayojan
Y0RAubIT6ms|||Bhajan Sri Krishna Chaitanya Prabhu Doya Koro More - 2023-09-06 - Sri Prem Prayojan
h4wvw6co094|||Bhajan Gāy Gorā Madhura Svare - 2023-08-31 - Sri Prem Prayojan
v5JjODERFLM|||Bhajan Śrī Daśāvatāra-stotram - 2023-08-31 - Sri Prem Prayojan
A7ylW94kjIg|||Bhajan (Yadi) Gauranga Nahito, Tabe Ki Hoito - 2023-07-01 - Sri Prem Prayojan
MeBH639cbac|||Bhajan Hari Bolibo Ar Madan-Mohan Heribo Go - 2023-07-02 - Sri Prem Prayojan
wnx7nDgvT_Y|||Bhajan Yamuna-Puline, Kadamba-Kanane - 2023-07-01 - Sri Prem Prayojan
eJWJsQmTR3A|||Bhajan Jaya Jaya Jagannatha Sacira Nandana - 2023-06-17 - Sri Prem Prayojan
zyuZRw50XRA|||Bhajan Davanala Sama (Sri Gurvastakam, Bengali) - 2022-06-17 - Sri Prem Prayojan
rvh8kxWtNmY|||Bhajan Ramani-Shiromani - 2023-01-16 - Sri Prem Prayojan
zFQevqrFYww|||Bhajan Kabe Habe Bolo Se-Dina Amar - 2023-01-16 - Sri Prem Prayojan
bTJmy-Stn-k|||Bhajan Radha Nama Parama Sukha-Dai - 2022-09-04 - Sri Prem Prayojan
laBce5FeNac|||Bhajan Sri Mangala-Gita - 2022-08-19 - Sri Prem Prayojan
Vmyue6YIwHU|||Bhajan Chhorato Purusha Abhiman - 2022-07-15 - Sri Prem Prayojan
Mb_NAOC5-cM|||Bhajan Yashomati Nandana - 2022-07-15 - Sri Prem Prayojan
35RQmHdbd3I|||Bhajan Mama Mana Mandire - 2022-07-13 - Sri Prem Prayojan
LsZy2yG4afw|||Bhajan Udilo Aruna - 2022-01-05 - Sri Prem Prayojan
MT65vbuKULc|||Bhajan Jhula Jhule Radha-Damodara - 2021-08-18 - Sri Prem Prayojan
rb2kE4FQvIE|||Bhajan Radhe Jhulana Padharo - 2021-08-18 - Sri Prem Prayojan
k89PcScU1C0|||Bhajan Jaya Jaya Vallabha-Raja-Kumara - 2021-05-28 - Sri Prem Prayojan
voAXCiJ04y8|||Bhajan Yan Kali Rupa - 2020-08-02 - Sri Prem Prayojan
zYV3s49wGGk|||Bhajan Radhe Jaya Jaya Madhava Dayite at Radha Kunda - 2020-02-27 - Sri Prem Prayojan
MtKi-9d2etg|||Bhajan Jaya Jaya Sri Guru at Samadhi of Srila Narayana Maharaja - 2020-02-27 - Sri Prem Prayojan
IVQpfgw3pWI|||Bhajan Ke Jabi Ke Jabi on the Boat - 2020-02-27 - Sri Prem Prayojan
Oep65u0erDM|||Bhajan Vraja Jana Mana Sukhakari - 2019-08-25 - Sri Prem Prayojan
CTdRROGqGMY|||Bhajan Manasa Deho Geho - 2019-07-17 - Sri Prem Prayojan
IAtesIV7ZuE|||Bhajan Jaya Radha Madhava - 2019-05-06 - Sri Prem Prayojan
ZrtZ9R26pS4|||Bhajan Ha Ha Mora Gaura-Kishora - 2019-03-03 - Sri Prem Prayojan
JK6zIb89BA0|||Bhajan Sakhe Kalaya Gauram Udaram - 2019-02-10 - Sri Prem Prayojan
a3Y_v6G-Gjk|||Bhajan Radhe Jaya Jaya Madhava-Dayite - 2019-01-19 - Sri Prem Prayojan
cbHKEN7FVsM|||Bhajan Krishna Deva Bhavantam Vande - 2019-01-19 - Sri Prem Prayojan
6eyyNjXFlYA|||Bhajan Devadi-Deva Gaurachandra - 2019-01-19 - Sri Prem Prayojan
sXwq0P0J3jY|||Bhajan Anupama Madhuri Jodi - 2019-01-04 - Sri Prem Prayojan
dKNFJ5BP_fo|||Bhajan Sri Krishna Chaitanya Prabhu Doya Koro More - 2019-01-03 - Sri Prem Prayojan
8rlqrH31vQc|||Bhajan Vande Vishvambhara - 2019-01-02 - Sri Prem Prayojan
W63UGrjJ2Sk|||Bhajan Jaya Radha-Madhava - 2019-01-02 - Sri Prem Prayojan
Xg49eKivnPo|||Bhajan Je Anilo Prema-Dhana - 2018-12-30 - Sri Prem Prayojan
Wio_Ebpwa5E|||Bhajan Vande Vishvambhara - 2018-12-30 - Sri Prem Prayojan
BEn4C0zLttU|||Bhajan Jaya Jaya Sundara Nanda-Kumara - 2018-12-30 - Sri Prem Prayojan
Vyz48Zp7QN8|||Bhajan Gauridasa-Mandire - 2018-10-06 - Sri Prem Prayojan
sAanLBcrQxw|||Bhajan Vasatu Mano Mama Madana-Gopale - 2018-08-11 - Sri Prem Prayojan
smfOoU-q2hQ|||Bhajan Gay Gora Madhura Svare - 2018-08-26 - Sri Prem Prayojan
e9BgMS_shkE|||Bhajan Vasatu Mano Mama Madana-Gopale - 2018-08-26 - Sri Prem Prayojan
4WDRV0CIU-A|||Bhajan Anupama Madhuri Jodi - 2018-08-25 - Sri Prem Prayojan
GAQqkvMkUkU|||Bhajan Kali-Kukkura - 2018-08-25 - Sri Prem Prayojan
bmfTttLaTfE|||Bhajan Radha-Kunda-Tata - 2018-08-25 - Sri Prem Prayojan
45JZhdTT4gc|||Bhajan Ke Jabi Ke Jabi Re Bhai - 2018-08-25 - Sri Prem Prayojan
Hyd2q54gOiw|||Bhajan Sri Krishna Chaitanya Prabhu Doya Koro More - 2018-08-24 - Sri Prem Prayojan
PwhKUfZX5ho|||Bhajan Radha-Krishna Prana Mora - 2018-08-24 - Sri Prem Prayojan
4nElJfnMsSY|||Bhajan Hari Bole Moder Gaura Elo - 2018-08-24 - Sri Prem Prayojan
RV5J7JAqslQ|||Bhajan Yan Kali Rupa - 2018-08-23 - Sri Prem Prayojan
3F3x6V4rDUo|||Bhajan Jaya Jaya Sundara Nanda-Kumara - 2018-08-23 - Sri Prem Prayojan
mOk7MWZ0IP0|||Bhajan Sri Gaura-Rupa-Guna-Varnana - 2018-08-22 - Sri Prem Prayojan
Phe9GE0uDc4|||Bhajan Sri Mangala-Gita - 2018-08-22 - Sri Prem Prayojan
Qd3noP888ow|||Bhajan Hari Bole Moder Gaura Elo - 2018-08-09 - Sri Prem Prayojan
1we-8eOaI7o|||Bhajan Jaya Jaya Sundara Nanda-Kumara - 2018-08-08 - Sri Prem Prayojan
Q_TpTESWrFI|||Bhajan Jaya Jaya Sri Guru Prema-Kalpataru - 2018-07-01 - Sri Prem Prayojan
mU4mKZw3icA|||Bhajan Radha-Kunda-Tata - 2018-06-30 - Sri Prem Prayojan
4xdXFQG0r9w|||Bhajan Jaya Jaya Sundara Nanda-Kumara - 2018-06-30 - Sri Prem Prayojan
VuBDcJ_WHaw|||Bhajan Krishna Deva Bhavantam Vande + Radhe Jaya Madhava Dayite - 2018-06-29 - Sri Prem Prayojan
HN2yi8dFOzU|||Bhajan Hari Bole Moder Goura Elo - 2018-06-29 - Sri Prem Prayojan
OGgPUwgnk4E|||Bhajan Namami-Nanda-Nandanam + Sri Radha-Kripa-Kataksha-Stava-Raja - 2018-06-28 - Sri Prem Prayojan
xUgLsvBhfk4|||Bhajan Radha-Krishna Prana Mora - 2018-06-27 - Sri Prem Prayojan
L2-NyMoL2H8|||Bhajan Devadi-Deva Gaurachandra - 2018-06-27 - Sri Prem Prayojan
zsvAr9PKw_g|||Bhajan Anupama Madhuri Jodi - 2018-06-27 - Sri Prem Prayojan
Jqk2mHYPT0g|||Bhajan Gopinatha, Mama Nivedana Suno - 2018-06-17 - Sri Prem Prayojan"""


def normalize(text):
    """Normalize text: NFD decompose, remove diacritics, lowercase, keep only alphanum+space."""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower()
    text = re.sub(r"[''`\u2019\u2018\u02bc]", '', text)   # apostrophes
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_bhajan_name(yt_title):
    """Extract clean bhajan name from YouTube title."""
    t = yt_title
    # Remove leading "Bhajan " / "Bhajans "
    t = re.sub(r'^Bhajan[s]?\s+', '', t, flags=re.IGNORECASE)
    # Remove "Sri Prem Prayojan" anywhere
    t = re.sub(r'[-–]?\s*Sri Prem Prayojan\s*[-–]?', ' ', t, flags=re.IGNORECASE)
    # Remove date patterns like "- 2024-07-21 -" or "2022-05-28"
    t = re.sub(r'[-–]?\s*\d{4}-\d{2}-\d{2}\s*[-–]?', ' ', t)
    # Remove trailing context like " at Radha Kunda...", " on the Boat", " in one Raga", " with explanation"
    t = re.sub(r'\s+(at |on the |in one |with |in |in Puria)\w.*$', '', t, flags=re.IGNORECASE)
    # Remove " by Śrīla..." author attribution
    t = re.sub(r'\s+by\s+.+$', '', t, flags=re.IGNORECASE)
    # Remove parenthetical "Sri Guru-Parampara (Krishna Hoite...)" — keep what's outside parens if it's the main title
    # But keep "(Hari) Haraye..." style where paren is part of title
    # Heuristic: if text before paren is short (<15 chars without paren), try both
    # Remove " + second bhajan" if combined video
    t = re.sub(r'\s*\+\s*.+$', '', t)
    t = t.strip(' -–,')
    return t


def similarity(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def main():
    # Load bhajan titles from Excel
    df = pd.read_excel('Bhajans.xlsx')
    db_titles = sorted(df['Bhajan_Title'].dropna().unique().tolist())
    print(f"Bhajan DB: {len(db_titles)} titles\n")

    # Parse playlist (newest first)
    playlist = []
    for line in RAW_PLAYLIST.strip().split('\n'):
        if '|||' not in line:
            continue
        vid, yt_title = line.split('|||', 1)
        bhajan_name = extract_bhajan_name(yt_title.strip())
        playlist.append((vid.strip(), bhajan_name, yt_title.strip()))

    # Match: for each playlist item, find best DB title
    # Skip if DB title already matched (keep newest)
    THRESHOLD = 0.60
    matched = {}        # db_title -> (vid, score, yt_name)
    unmatched = []

    for vid, bhajan_name, yt_title in playlist:
        best_title = None
        best_score = 0
        for db_title in db_titles:
            s = similarity(bhajan_name, db_title)
            if s > best_score:
                best_score = s
                best_title = db_title

        if best_score >= THRESHOLD:
            if best_title not in matched:
                matched[best_title] = (vid, best_score, bhajan_name)
            # else: already have newer video, skip
        else:
            unmatched.append((vid, bhajan_name, best_score, best_title))

    # Print results
    print(f"{'='*70}")
    print(f"MATCHED: {len(matched)} bhajans")
    print(f"{'='*70}")
    for db_title, (vid, score, yt_name) in sorted(matched.items()):
        print(f"  [{score:.0%}] {db_title}")
        print(f"         YT: {yt_name}")
        print(f"         ID: {vid}")

    print(f"\n{'='*70}")
    print(f"UNMATCHED from playlist: {len(unmatched)}")
    print(f"{'='*70}")
    for vid, name, score, closest in unmatched:
        print(f"  {name}  (best: {closest} @ {score:.0%})")

    # Generate YOUTUBE_IDS dict for generate_html.py
    print(f"\n{'='*70}")
    print("YOUTUBE_IDS for generate_html.py:")
    print(f"{'='*70}")
    print("const YOUTUBE_IDS = {")
    for db_title, (vid, score, _) in sorted(matched.items()):
        escaped = db_title.replace('\\', '\\\\').replace('"', '\\"')
        print(f'  "{escaped}": "{vid}",')
    print("};")

    # Also save as Python dict for easy copy-paste
    print(f"\n{'='*70}")
    print("Python dict:")
    print(f"{'='*70}")
    print("YOUTUBE_IDS = {")
    for db_title, (vid, score, _) in sorted(matched.items()):
        escaped = db_title.replace("'", "\\'")
        print(f"    '{escaped}': '{vid}',")
    print("}")


if __name__ == '__main__':
    main()
