#!/usr/bin/env python
"""
parse_excel.py — Regenerate data/streams.json from the source workbook.

Usage:
    python parse_excel.py [path-to-xlsx]

Defaults to "Full Table List (Updated 05.11.26).xlsx" in the same folder.

Applies data-cleaning fixes on top of the raw parse:
  * strip whitespace from every value
  * normalize category names (Live DragonTiger -> Dragon Tiger, etc.)
  * normalize partner names to title case (EEZE -> Eeze, EZUGI -> Ezugi)
  * blank out placeholder Religa locations (-4 / -3 / -2)
  * fix the Eeze "StudioSic Bo" missing-space typo
  * map switcher True -> Yes, N/A -> No
  * strip junk query params from stream URLs (keep only group.id)
"""
import json
import os
import re
import sys

import openpyxl

CATEGORY_MAP = {
    "branded roulette": "Branded Roulette",
    "live dragontiger": "Dragon Tiger",
    "livedragontiger": "Dragon Tiger",
    "dragontiger": "Dragon Tiger",
    "live dragon tiger": "Dragon Tiger",
    "liveroulette": "Live Roulette",
    "roulette": "Live Roulette",
}


# Exact name corrections (typos / all-caps). Applied to Religa game names.
NAME_MAP = {
    "MAHNJONG": "Mahjong",
    "Fortune DROP": "Fortune Drop",
    "Dice VIP Roullete": "Dice VIP Roulette",
    "VIVO Branded Roulette European Auto Roulette": "Vivo Branded Roulette European Auto Roulette",
}


def norm_name(raw):
    n = clean(raw)
    if n is None:
        return None
    return NAME_MAP.get(n, n)


def clean(s):
    if s is None:
        return None
    s = str(s).strip()
    return s if s else None


def norm_category(raw):
    c = clean(raw)
    if not c:
        return None
    key = c.lower().replace("  ", " ")
    return CATEGORY_MAP.get(key, c)


def norm_partner(raw):
    p = clean(raw)
    if not p:
        return None
    if p.upper() == "S.A":
        return "S.A"
    return p.title()


def norm_location(raw, sheet):
    loc = clean(raw)
    if not loc:
        return None
    if sheet == "Religa" and re.fullmatch(r"-?\d+", loc):
        return None
    if "StudioSic Bo" in loc:
        loc = loc.replace("StudioSic Bo", "Studio Sic Bo")
    return loc


def norm_switcher(raw):
    s = clean(raw)
    if s is None:
        return None
    low = s.lower()
    if low in ("true", "yes", "y"):
        return "Yes"
    if low in ("false", "no", "n", "n/a"):
        return "No"
    return s


def clean_url(raw):
    """Strip junk query params from a stream URL.

    Keeps only ``group.id`` (required by the nanoplayer embed URLs to select
    the stream). Drops expired ``security.jwtoken``, transcoding ``vtrans*`` /
    ``startIndex``, analytics (``_gl`` / ``_ga`` / ``_gcl_au``) and player
    options (``autoplay`` / ``muted`` / ``playsinline``).
    """
    u = clean(raw)
    if not u:
        return None
    base, sep, query = u.partition("?")
    if not sep:
        return base
    kept = []
    for part in query.split("&"):
        key = part.split("=", 1)[0]
        if key == "group.id":
            kept.append(part)
    if kept:
        return base + "?" + "&".join(kept)
    return base


def to_playout_url(url):
    """Return the clean playout URL for a stream.

    If the stored URL is a nanoplayer embed (has group.id=<uuid>), convert it to
    the full dashboard playout page. Otherwise return as-is.

    The playout page is always served from ``dashboard.nanostream.cloud`` — the
    ``bintu-cloud-frontend.nanocosmos.de`` variant of the same /playout/<uuid>
    path redirects to a login wall, so any such URL is rewritten to the
    nanostream domain (which plays without authentication).
    """
    if not url:
        return url
    m = re.search(r"group\.id=([0-9a-fA-F-]{36})", url)
    if m:
        return f"https://dashboard.nanostream.cloud/playout/{m.group(1)}"
    m = re.search(r"/playout/([0-9a-fA-F-]{36})", url)
    if m:
        return f"https://dashboard.nanostream.cloud/playout/{m.group(1)}"
    return url


def stream_uuid(url):
    """Extract the stream UUID from a playout or nanoplayer-embed URL, else None."""
    if not url:
        return None
    m = re.search(r"group\.id=([0-9a-fA-F-]{36})", url)
    if m:
        return m.group(1)
    m = re.search(r"/playout/([0-9a-fA-F-]{36})", url)
    if m:
        return m.group(1)
    return None


# Stream UUIDs whose duplicate rows should be merged into a single entry.
# For each, the row that carries client IDs is kept; the ID-less duplicate is
# dropped. (Other duplicate-UUID rows — e.g. Saturn / Live Football — are left
# as separate rows on purpose.)
MERGE_DUPLICATE_UUIDS = {
    "81193ed4-9c6e-4da8-9e23-cd1f459268fb",  # Vivo Branded European Auto Roulette
}


def merge_duplicate_streams(rows):
    """Collapse rows that share a stream UUID listed in MERGE_DUPLICATE_UUIDS.

    Keeps the row that has the most client IDs (the 'real' one) and drops the
    rest. Returns (merged_rows, dropped_names).
    """
    by_uuid = {}
    for r in rows:
        u = stream_uuid(r.get("url"))
        if u in MERGE_DUPLICATE_UUIDS:
            by_uuid.setdefault(u, []).append(r)

    keep, dropped = [], []
    merged_uuids = set()
    for r in rows:
        u = stream_uuid(r.get("url"))
        if u in MERGE_DUPLICATE_UUIDS:
            if u in merged_uuids:
                dropped.append(r["name"])
                continue
            merged_uuids.add(u)
            # keep the richest row (most client IDs) among this uuid's rows
            group = by_uuid[u]
            def id_count(x):
                return sum(1 for k in x if k.endswith("_id"))
            best = max(group, key=id_count)
            keep.append(best)
        else:
            keep.append(r)
    return keep, dropped


def parse_religa(ws):
    out = []
    for r in range(3, ws.max_row + 1):
        name = norm_name(ws.cell(r, 3).value)
        if not name:
            continue
        link_cell = ws.cell(r, 9)
        url = clean_url(link_cell.hyperlink.target if link_cell.hyperlink else None)
        playout = to_playout_url(url) if url else None
        entry = {
            "name": name,
            "url": url,
            "playout_url": playout if playout and playout != url else None,
            "category": norm_category(ws.cell(r, 2).value),
            "switcher": norm_switcher(ws.cell(r, 10).value),
            "religa_id": clean(ws.cell(r, 4).value),
            "ezugi_id": clean(ws.cell(r, 5).value),
            "vivo_id": clean(ws.cell(r, 6).value),
            "lucky_streak_id": clean(ws.cell(r, 7).value),
            "alg_id": clean(ws.cell(r, 8).value),
            "partner": norm_partner(ws.cell(r, 11).value),
            "location": norm_location(ws.cell(r, 12).value, "Religa"),
            "country": clean(ws.cell(r, 14).value),
            "local_remote": clean(ws.cell(r, 13).value),
        }
        out.append({k: v for k, v in entry.items() if v is not None})
    out, dropped = merge_duplicate_streams(out)
    for n in dropped:
        print(f"  [merge] dropped duplicate row: {n!r}")
    return out


def parse_simple(ws, sheet):
    out = []
    for r in range(3, ws.max_row + 1):
        tid = clean(ws.cell(r, 3).value)
        if not tid:
            continue
        entry = {
            "name": tid,
            "table_id": tid,
            "category": norm_category(ws.cell(r, 2).value),
            "partner": norm_partner(ws.cell(r, 4).value),
            "location": norm_location(ws.cell(r, 5).value, sheet),
            "local_remote": clean(ws.cell(r, 6).value),
        }
        out.append({k: v for k, v in entry.items() if v is not None})
    return out


def main():
    default = "Full Table List (Updated 05.11.26).xlsx"
    path = sys.argv[1] if len(sys.argv) > 1 else default
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

    wb = openpyxl.load_workbook(path, data_only=True)
    sheets = {}
    if "Religa" in wb.sheetnames:
        sheets["Religa"] = parse_religa(wb["Religa"])
    if "Eeze" in wb.sheetnames:
        sheets["Eeze"] = parse_simple(wb["Eeze"], "Eeze")
    if "Red Panda" in wb.sheetnames:
        sheets["Red Panda"] = parse_simple(wb["Red Panda"], "Red Panda")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "streams.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"sheets": sheets}, f, indent=2, ensure_ascii=False)
        f.write("\n")

    total = sum(len(v) for v in sheets.values())
    print(f"Wrote {out_path}")
    for k, v in sheets.items():
        print(f"  {k}: {len(v)}")
    print(f"  total: {total}")


if __name__ == "__main__":
    main()
