# -*- coding: utf-8 -*-
"""
build_presets.py — Generate the dedicated preset pages (game-shows.html, ezugi.html)
from data/streams.json. Each page shows a grid of video cards (embedded iframes)
with live status. Re-run after re-parsing the Excel to keep them in sync.

    python build_presets.py
"""
import json
import os
import html

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(BASE, "data", "streams.json"), encoding="utf-8"))
RELIGA = DATA["sheets"]["Religa"]

EMBED_BASE = "https://demo.nanocosmos.de/nanoplayer/embed/2.0.0/nanoplayer.html"


def to_embed_url(url):
    """Convert a playout URL to a clean nanoplayer embed URL (no dashboard chrome).

    - /playout/<uuid>  -> EMBED_BASE?group.id=<uuid>&autoplay=true&muted=true&style.displayMutedAutoplay=false
    - already an embed (has group.id=) -> add autoplay/muted/displayMutedAutoplay if missing
    - anything else -> return as-is

    ``style.displayMutedAutoplay=false`` hides the player's centered "tap to unmute"
    overlay while the stream stays muted (playback.automute is left at its default true).
    """
    if not url:
        return url
    import re
    m = re.search(r"/playout/([0-9a-fA-F-]{36})", url)
    if m:
        return f"{EMBED_BASE}?group.id={m.group(1)}&autoplay=true&muted=true&style.displayMutedAutoplay=false"
    if "group.id=" in url:
        sep = "&" if "?" in url else "?"
        extra = []
        if "autoplay=" not in url:
            extra.append("autoplay=true")
        if "muted=" not in url:
            extra.append("muted=true")
        if "displayMutedAutoplay=" not in url:
            extra.append("style.displayMutedAutoplay=false")
        if extra:
            return url + sep + "&".join(extra)
        return url
    return url


def to_playout_url(url):
    """Return the clean playout URL (full dashboard page) for the "Open" link.

    - nanoplayer embed (has group.id=<uuid>) -> dashboard.nanostream.cloud/playout/<uuid>
    - already a /playout/<uuid> URL -> rewrite to the nanostream domain
    - anything else -> return as-is

    The playout page is always served from ``dashboard.nanostream.cloud`` — the
    ``bintu-cloud-frontend.nanocosmos.de`` variant of the same /playout/<uuid>
    path redirects to a login wall, so it is rewritten to the nanostream domain
    (which plays without authentication).
    """
    if not url:
        return url
    import re
    m = re.search(r"group\.id=([0-9a-fA-F-]{36})", url)
    if m:
        return f"https://dashboard.nanostream.cloud/playout/{m.group(1)}"
    m = re.search(r"/playout/([0-9a-fA-F-]{36})", url)
    if m:
        return f"https://dashboard.nanostream.cloud/playout/{m.group(1)}"
    return url

# Preset definitions: (filename, title, subtitle, predicate)
PRESETS = [
    ("game-shows.html", "Game Shows", "Game Show tables",
     lambda e: e.get("category") == "Game Show"),
    ("ezugi.html", "Ezugi", "Tables streamed to Ezugi",
     lambda e: e.get("partner") == "Ezugi"),
]

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script>
        (function () {{
            var t = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            document.documentElement.setAttribute('data-theme', t);
        }})();
    </script>
    <link rel="stylesheet" href="style.css">
    <style>
        html {{ scrollbar-gutter: stable; }}  /* reserve scrollbar space so the topbar nav stays put across pages */
        .topbar {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            gap: 16px;
            margin-bottom: 14px;
        }}
        .topbar-title {{
            margin: 0;
            font-size: 1.4em;
            white-space: nowrap;
            justify-self: start;
        }}
        .topbar-nav {{
            justify-self: center;
        }}
        .topbar-toggle {{
            justify-self: end;
        }}
        .preset-header {{
            display: flex; align-items: baseline; gap: 12px;
            margin: 18px 0 6px; flex-wrap: wrap;
        }}
        .preset-header h1 {{ font-size: 1.5em; margin: 0; }}
        .preset-header .sub {{ color: var(--text-light); font-size: 0.95em; }}
        .preset-count {{
            background: var(--primary-color); color: #fff;
            border-radius: 12px; padding: 2px 10px; font-weight: 700; font-size: 0.9em;
        }}
        .preset-toolbar {{ margin: 10px 0 16px; }}
        .preset-grid {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 16px;
        }}
        .preset-card {{
            flex: 0 1 380px;
            min-width: 300px;
            background: var(--card-background);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            box-shadow: var(--shadow);
            overflow: hidden;
            display: flex; flex-direction: column;
        }}
        .preset-card-head {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 10px 12px; gap: 8px;
            border-bottom: 1px solid var(--border-color);
        }}
        .preset-name {{ font-weight: 700; font-size: 0.95em; }}
        .preset-frame-wrap {{
            position: relative; width: 100%;
            aspect-ratio: 16 / 9;
            background: #000;
        }}
        .preset-frame {{
            position: absolute; inset: 0;
            width: 100%; height: 100%;
            border: 0;
        }}
        .preset-nolink {{
            position: absolute; inset: 0;
            display: flex; align-items: center; justify-content: center;
            color: #888; font-size: 0.9em;
        }}
        .preset-card-foot {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 8px 12px; gap: 8px;
            border-top: 1px solid var(--border-color);
        }}
        .preset-meta {{ color: var(--text-light); font-size: 0.8em; }}
        .preset-open {{
            color: var(--primary-color); text-decoration: none; font-size: 0.85em; font-weight: 600;
        }}
        .preset-open:hover {{ text-decoration: underline; }}

        .preset-nav {{
            display: flex;
            gap: 8px;
        }}
        .preset-nav a.preset-link {{
            display: inline-block;
            box-sizing: border-box;
            min-width: 104px;
            text-align: center;
            color: var(--primary-color);
            background-color: var(--card-background);
            text-decoration: none;
            font-size: 0.85em;
            font-weight: 600;
            padding: 6px 14px;
            border: 1px solid var(--border-color);
            border-radius: 16px;
            transition: background 0.15s, color 0.15s, border-color 0.15s;
        }}
        .preset-nav a.preset-link:hover {{
            background: var(--primary-color);
            border-color: var(--primary-color);
            color: #fff;
        }}
        .preset-nav a.preset-link.active {{
            background: var(--primary-color);
            border-color: var(--primary-color);
            color: #fff;
        }}

        /* buttons (match the main dashboard) */
        #dark-mode-toggle {{
            padding: 7px 16px;
            border: 1px solid var(--border-color);
            background-color: var(--card-background);
            color: var(--text-color);
            border-radius: 18px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: background-color 0.2s, border-color 0.2s, color 0.2s;
        }}
        #dark-mode-toggle:hover {{
            border-color: var(--primary-color);
            color: var(--primary-color);
            background-color: rgba(0,123,255,0.06);
        }}
        .btn-ghost {{
            background-color: var(--card-background);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 7px 14px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s, border-color 0.2s, color 0.2s;
        }}
        .btn-ghost:hover {{
            background-color: rgba(0,123,255,0.08);
            border-color: var(--primary-color);
            color: var(--primary-color);
        }}
        .btn-ghost.toggle.active {{
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            color: #fff;
        }}
        .btn-ghost.toggle.active:hover {{
            background-color: #0056b3;
            border-color: #0056b3;
            color: #fff;
        }}
        .preset-card.hidden {{ display: none; }}

        /* status badges (same palette as the search dashboard) */
        .status {{
            display: inline-flex; align-items: center; gap: 5px;
            padding: 3px 8px; border-radius: 10px;
            font-size: 0.72em; font-weight: 700; letter-spacing: 0.3px; white-space: nowrap;
        }}
        .status .dot {{ width: 7px; height: 7px; border-radius: 50%; background: currentColor;
            animation: pulse 1.4s ease-in-out infinite; }}
        @keyframes pulse {{ 0%,100% {{ opacity:1; transform:scale(1); }} 50% {{ opacity:.35; transform:scale(.7); }} }}
        .status.live {{ background: rgba(39,174,96,0.15); color: #27ae60; }}
        .status.offline {{ background: rgba(231,76,60,0.15); color: #e74c3c; }}
        .status.nostream {{ background: rgba(149,165,166,0.18); color: #95a5a6; }}
        .status.checking {{ background: rgba(243,156,18,0.15); color: #f39c12; }}
        .status.error {{ background: rgba(231,76,60,0.15); color: #e74c3c; }}
        [data-theme="dark"] .status.live {{ background: rgba(39,174,96,0.22); color: #2ecc71; }}
        [data-theme="dark"] .status.offline {{ background: rgba(231,76,60,0.22); color: #ff6b5e; }}
        [data-theme="dark"] .status.nostream {{ background: rgba(149,165,166,0.22); color: #bdc3c7; }}
        [data-theme="dark"] .status.checking {{ background: rgba(243,156,18,0.22); color: #f5b041; }}
        [data-theme="dark"] .status.error {{ background: rgba(231,76,60,0.22); color: #ff6b5e; }}
    </style>
</head>
<body>
    <div class="page-wrap">
        <div class="topbar">
            <h1 class="topbar-title">{title}</h1>
            <nav class="preset-nav topbar-nav">{nav}</nav>
            <button id="dark-mode-toggle" class="topbar-toggle" title="Toggle dark mode">🌙</button>
        </div>
        <div class="preset-header">
            <span class="sub">{subtitle}</span>
            <span class="preset-count" id="preset-count"></span>
        </div>
        <div class="preset-toolbar">
            <button id="refresh-status" class="btn btn-ghost">&#10227; Refresh status</button>
            <button id="hide-offline" class="btn btn-ghost toggle" title="Show or hide tables that are not currently streaming">&#9746; Hide offline</button>
        </div>
        <div class="preset-grid" id="preset-grid"></div>
    </div>

    <script>
        window.__PRESET_STREAMS__ = {streams_json};
    </script>
    <script src="js/dark-mode.js"></script>
    <script src="js/preset.js"></script>
</body>
</html>
"""

def build():
    NAV_PAGES = [
        ("search-dashboard.html", "Search"),
        ("game-shows.html", "Game Shows"),
        ("ezugi.html", "Ezugi"),
    ]
    for filename, title, subtitle, pred in PRESETS:
        streams = [e for e in RELIGA if pred(e)]
        for e in streams:
            e["embed"] = to_embed_url(e.get("url"))
            e["playout"] = to_playout_url(e.get("url"))
        nav = "".join(
            f'<a href="{href}" class="preset-link{" active" if href == filename else ""}">{label}</a>'
            for href, label in NAV_PAGES
        )
        page = PAGE.format(
            title=html.escape(title),
            subtitle=html.escape(subtitle),
            nav=nav,
            streams_json=json.dumps(streams, ensure_ascii=False),
        )
        out = os.path.join(BASE, filename)
        with open(out, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"wrote {filename}  ({len(streams)} streams)")

if __name__ == "__main__":
    build()
