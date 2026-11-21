#!/usr/bin/env python
"""
check_streams.py — Verify each stream URL actually resolves to a video stream.

Method: extract the nanoStream stream ID from the playout URL (either
``group.id=<uuid>`` for nanoplayer embeds or ``/playout/<uuid>``), then query
the public bintu metadata API:

    https://bintu.nanostream.cloud/stream/<uuid>

The response has a ``state`` field:
    live    -> actively streaming video (resolves to a video stream)
    ended   -> stream exists but is not currently live
    (other) -> anything else is reported as-is

It also reports whether an HLS playlist URL is present.

Writes data/stream-check-YYYY-MM-DD.json and prints a summary.
"""
import json
import os
import re
import ssl
import concurrent.futures
import urllib.request
import urllib.error
from datetime import date

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()
OPENER = urllib.request.build_opener(urllib.request.HTTPSHandler(context=SSL_CTX))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BINTU = "https://bintu.nanostream.cloud/stream/"


def extract_id(url):
    m = re.search(r"group\.id=([0-9a-fA-F-]{36})", url)
    if m:
        return m.group(1)
    m = re.search(r"/playout/([0-9a-fA-F-]{36})", url)
    if m:
        return m.group(1)
    return None


def check(url):
    sid = extract_id(url)
    if not sid:
        return {"stream_id": None, "state": None, "has_hls": False,
                "note": "no stream ID in URL (portal/external link)"}
    try:
        req = urllib.request.Request(BINTU + sid, headers=UA)
        with OPENER.open(req, timeout=20) as r:
            d = json.loads(r.read().decode("utf-8", "ignore"))
        state = d.get("state")
        h5 = (d.get("playout") or {}).get("h5live") or []
        has_hls = bool(h5 and h5[0].get("server", {}).get("hls"))
        return {"stream_id": sid, "state": state, "has_hls": has_hls,
                "type": d.get("type"), "note": None}
    except urllib.error.HTTPError as e:
        return {"stream_id": sid, "state": None, "has_hls": False,
                "note": f"HTTP {e.code}"}
    except Exception as e:
        return {"stream_id": sid, "state": None, "has_hls": False,
                "note": f"{type(e).__name__}: {e}"}


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    data = json.load(open(os.path.join(base, "data", "streams.json"), encoding="utf-8"))

    tasks = []
    for sheet, entries in data["sheets"].items():
        for e in entries:
            tasks.append((sheet, e.get("name"), e.get("url")))

    def worker(t):
        sheet, name, url = t
        res = check(url) if url else {"stream_id": None, "state": None,
                                       "has_hls": False, "note": "no URL"}
        res.update({"sheet": sheet, "name": name, "url": url})
        return res

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for res in ex.map(worker, tasks):
            results.append(res)
            st = res.get("state")
            if st == "live":
                mark = "LIVE"
            elif st == "ended":
                mark = "ended"
            elif st is None:
                mark = "n/a "
            else:
                mark = str(st)
            print(f"  [{mark:5}] {res['sheet']:10} {str(res['name'])[:32]:32} "
                  f"hls={'Y' if res.get('has_hls') else 'N'} {res.get('note') or ''}",
                  flush=True)

    out = os.path.join(base, "data", f"stream-check-{date.today().isoformat()}.json")
    json.dump(results, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    live = [r for r in results if r.get("state") == "live"]
    ended = [r for r in results if r.get("state") == "ended"]
    other = [r for r in results if r.get("state") not in ("live", "ended", None)]
    noid = [r for r in results if r.get("stream_id") is None]
    print("\n" + "=" * 72)
    print(f"TOTAL {len(results)}  |  LIVE {len(live)}  |  ENDED {len(ended)}  |  "
          f"OTHER {len(other)}  |  NO-ID/NO-URL {len(noid)}")
    print("=" * 72)
    if ended:
        print("\nENDED (not currently streaming):")
        for r in ended:
            print(f"  {r['sheet']:8} {str(r['name'])[:32]}")
    if other:
        print("\nOTHER STATES:")
        for r in other:
            print(f"  {r['sheet']:8} {str(r['name'])[:32]} state={r.get('state')}")
    if noid:
        print("\nNO STREAM ID / NO URL:")
        for r in noid:
            print(f"  {r['sheet']:8} {str(r['name'])[:32]}  {r.get('note')}  {r.get('url')}")
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
