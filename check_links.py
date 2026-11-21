#!/usr/bin/env python
"""
check_links.py — Verify every stream URL in data/streams.json.

For each URL it does an HTTP GET (following redirects) and records:
  * status code
  * whether it looks like a valid playout page (heuristic)
  * final URL after redirects
  * elapsed time

Writes results to data/link-check-YYYY-MM-DD.json and prints a summary table.
"""
import json
import os
import ssl
import sys
import time
import urllib.request
import urllib.error
import concurrent.futures
from datetime import date

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

OPENER = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=SSL_CTX)
)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# Hosts that are known playout/embed endpoints
PLAYOUT_HOSTS = (
    "dashboard.nanostream.cloud",
    "bintu-cloud-frontend.nanocosmos.de",
    "demo.nanocosmos.de",
    "play.wingene.games",
)


def check(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    t0 = time.time()
    try:
        with OPENER.open(req, timeout=timeout) as r:
            status = r.status
            final = r.url
            ctype = r.headers.get("Content-Type", "")
            body = r.read(4000)
            text = body.decode("utf-8", errors="ignore").lower()
            # Heuristic: a real playout page mentions the player / stream
            looks_ok = any(k in text for k in ("player", "stream", "video", "playout", "nanoplayer", "hls", "m3u8"))
            return {
                "status": status,
                "final_url": final,
                "content_type": ctype,
                "ok": status == 200,
                "looks_like_playout": looks_ok,
                "elapsed": round(time.time() - t0, 2),
            }
    except urllib.error.HTTPError as e:
        return {
            "status": e.code,
            "final_url": e.url,
            "content_type": e.headers.get("Content-Type", "") if e.headers else "",
            "ok": False,
            "looks_like_playout": False,
            "elapsed": round(time.time() - t0, 2),
            "error": f"HTTP {e.code}",
        }
    except urllib.error.URLError as e:
        return {
            "status": None,
            "final_url": url,
            "content_type": "",
            "ok": False,
            "looks_like_playout": False,
            "elapsed": round(time.time() - t0, 2),
            "error": f"URLError: {e.reason}",
        }
    except Exception as e:
        return {
            "status": None,
            "final_url": url,
            "content_type": "",
            "ok": False,
            "looks_like_playout": False,
            "elapsed": round(time.time() - t0, 2),
            "error": f"{type(e).__name__}: {e}",
        }


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    data = json.load(open(os.path.join(base, "data", "streams.json"), encoding="utf-8"))

    tasks = []
    for sheet, entries in data["sheets"].items():
        for e in entries:
            tasks.append((sheet, e.get("name"), e.get("url")))

    def worker(t):
        sheet, name, url = t
        if not url:
            return {"sheet": sheet, "name": name, "url": None,
                    "status": None, "ok": False, "error": "no URL"}
        res = check(url)
        res.update({"sheet": sheet, "name": name, "url": url})
        return res

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for res in ex.map(worker, tasks):
            results.append(res)
            mark = "OK " if res.get("ok") else "ERR"
            print(f"  [{mark}] {res['sheet']:10} {str(res['name'])[:30]:30} {res.get('status')} {res.get('elapsed')}s", flush=True)

    out_path = os.path.join(base, "data", f"link-check-{date.today().isoformat()}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    ok = [r for r in results if r.get("ok")]
    no_url = [r for r in results if r.get("error") == "no URL"]
    failed = [r for r in results if not r.get("ok") and r.get("error") != "no URL"]
    print("\n" + "=" * 70)
    print(f"TOTAL: {len(results)}   OK: {len(ok)}   NO-URL: {len(no_url)}   FAILED: {len(failed)}")
    print("=" * 70)
    if failed:
        print("\nFAILED (real link errors):")
        for r in failed:
            print(f"  {r['sheet']:10} {str(r['name'])[:30]:30} "
                  f"status={r.get('status')} err={r.get('error')} url={r.get('url')}")
    if no_url:
        print(f"\nNO-URL ({len(no_url)} entries, expected for Eeze/Red Panda):")
        for r in no_url:
            print(f"  {r['sheet']:10} {str(r['name'])[:30]}")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
