#!/usr/bin/env python
"""
refresh.py — One-command re-parse.

Re-reads the Excel workbook and regenerates everything downstream:

    data/streams.json          (via parse_excel.py)
    game-shows.html, ezugi.html (via build_presets.py)

Usage:
    python refresh.py                  # uses the default 05.11.26 workbook
    python refresh.py path\\to.xlsx    # or point at a different workbook

Run this whenever the source Excel changes. No background process needed.
"""
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_XLSX = "Full Table List (Updated 05.11.26).xlsx"


def run(script, extra_args=None):
    cmd = [sys.executable, os.path.join(BASE, script)] + (extra_args or [])
    print("\n$ " + " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"ERROR: {script} failed (exit {result.returncode}). Stopping.")


def main():
    xlsx_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if xlsx_arg:
        xlsx_arg = os.path.abspath(xlsx_arg)
    xlsx = xlsx_arg or DEFAULT_XLSX

    # 1. Warn if the workbook is open in Excel/LibreOffice (lock file present)
    lock = os.path.join(BASE, ".~lock." + os.path.basename(xlsx) + "#")
    if os.path.exists(lock):
        print(f"WARNING: {os.path.basename(xlsx)} appears to be open (lock file found).")
        print("         Close it and save first so the parser reads the latest data.\n")

    # 2. Re-parse the Excel -> data/streams.json
    run("parse_excel.py", [xlsx_arg] if xlsx_arg else [])

    # 3. Rebuild the preset pages from the fresh JSON
    run("build_presets.py")

    # 4. Summary
    data = json.load(open(os.path.join(BASE, "data", "streams.json"), encoding="utf-8"))
    counts = {k: len(v) for k, v in data["sheets"].items()}
    total = sum(counts.values())
    print("\n" + "=" * 50)
    print("Refresh complete.")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"  total: {total}")
    print("  Regenerated: data/streams.json, game-shows.html, ezugi.html")
    print("  Hard-refresh the dashboard (Ctrl+Shift+R) to see changes.")
    print("=" * 50)


if __name__ == "__main__":
    main()
