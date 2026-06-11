"""
update_meta_from_metabot.py — refresh data/vct_meta.json from MetaBot.GG (2026 ranked data)

MetaBot serves its agent tables as server-rendered HTML (no JS wall), so this
works with a plain HTTP request — no headless browser needed. Much simpler and
more reliable than the vstats scraper.

It reads the per-map agent table for each active 2026 map and writes
data/vct_meta.json in the structure the app expects:

    {
      "last_updated": "2026-06-11",
      "series": "MetaBot.GG · 2026 Ranked (All Ranks)",
      "meta_by_map": {
        "Corrode": { "Skye": {"win_rate": 63.0, "pick_rate": 0.3}, ... },
        ...
      }
    }

SETUP (one time):
    pip install requests beautifulsoup4 --break-system-packages

USAGE:
    cd C:\\Users\\kimma\\Documents\\valcompbuilder
    python tools\\update_meta_from_metabot.py              # all active maps
    python tools\\update_meta_from_metabot.py --dry-run    # preview only
    python tools\\update_meta_from_metabot.py --maps Haven Split

NOTE: polite 2-second delay between maps. Run once per patch/act.
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_PATH = os.path.join(BASE_DIR, "data", "vct_meta.json")

# 2026 Stage 1 active competitive pool (Patch 12.x)
# Masters London 2026 pool (Patch 12.10)
ACTIVE_MAPS = ["Ascent", "Breeze", "Fracture", "Haven", "Lotus", "Pearl", "Split"]
# Maps recently re-added with small/noisy samples — flagged "limited data"
THIN_DATA_THRESHOLD = 15000  # matches; below this = unreliable

AGENT_NAMES = {
    "Jett", "Raze", "Neon", "Reyna", "Phoenix", "Yoru", "Iso", "Waylay",
    "Omen", "Brimstone", "Viper", "Astra", "Clove", "Harbor", "Miks",
    "Sova", "Fade", "Breach", "Skye", "Gekko", "KAY/O", "Tejo",
    "Killjoy", "Cypher", "Sage", "Deadlock", "Chamber", "Vyse", "Veto",
}


def scrape_map(map_name: str) -> dict:
    """Fetch one map's agent table from MetaBot. Returns {agent: {win_rate, pick_rate}}."""
    import requests
    url = f"https://metabot.gg/en/valorant/map/{map_name}/agents"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CompBuilder/1.0)"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    html = resp.text

    result = {}
    # Capture the match-count for reliability flagging
    mc = re.search(r"Matches\s*([\d,]+)", html)
    match_count = int(mc.group(1).replace(",", "")) if mc else 0
    result["__match_count__"] = match_count
    # The "Complete Agent Statistics" table rows look like:
    #   | #1 | [...Skye...](...) | S | Initiator | 1.67 | 0 | 63.0% | 0.3% | ...
    # Match: AgentName ... Tier ... Role ... KDA ... matches ... WR% ... PR%
    row_re = re.compile(
        r'([A-Za-z/]+)\]\(https://metabot\.gg/en/valorant/agent/[^)]+\)\s*'
        r'\|\s*([SABCDF])\s*\|\s*(Duelist|Initiator|Controller|Sentinel)\s*\|\s*'
        r'[\d.]+\s*\|\s*\d+\s*\|\s*([\d.]+)%\s*\|\s*([\d.]+)%'
    )
    for m in row_re.finditer(html):
        name = m.group(1).strip()
        if name in AGENT_NAMES:
            wr = float(m.group(4))
            pr = float(m.group(5))
            # First occurrence = the "All" (combined) table; skip attack/defense dupes
            if name not in result:
                result[name] = {"win_rate": wr, "pick_rate": pr}
    return result


def _is_reliable(map_data: dict) -> bool:
    return map_data.get("__match_count__", 0) >= THIN_DATA_THRESHOLD


def run(maps, dry_run=False):
    try:
        import requests  # noqa
    except ImportError:
        print("Missing 'requests'. Run: pip install requests beautifulsoup4 --break-system-packages")
        sys.exit(1)

    all_data = {}
    for i, m in enumerate(maps):
        print(f"[{i+1}/{len(maps)}] {m}...", end=" ", flush=True)
        try:
            data = scrape_map(m)
            if data:
                mc = data.pop("__match_count__", 0)
                all_data[m] = data
                flag = "" if mc >= THIN_DATA_THRESHOLD else "  [LIMITED DATA - thin sample]"
                print(f"OK {len(data)} agents ({mc:,} matches){flag}")
            else:
                print("no rows (layout may have changed)")
        except Exception as e:
            print(f"ERROR {e}")
        time.sleep(2.0)

    if not all_data:
        print("Nothing scraped.")
        sys.exit(1)

    # Merge with any existing maps (so out-of-rotation maps stay as backup)
    existing = {}
    if os.path.exists(META_PATH):
        try:
            existing = json.load(open(META_PATH, encoding="utf-8")).get("meta_by_map", {})
        except Exception:
            pass
    existing.update(all_data)

    # Reliability flags: maps with thin samples (recently rotated in)
    reliability = {}
    for m, d in all_data.items():
        # We popped match count already; re-derive reliability from a sentinel
        reliability[m] = True  # default; thin ones flagged during scrape print
    out = {
        "last_updated": date.today().isoformat(),
        "series": "MetaBot.GG · 2026 Ranked (Masters London pool)",
        "note": "Win/pick rates from MetaBot ranked data. Recently-rotated maps may show 'limited data'.",
        "active_maps": ACTIVE_MAPS,
        "thin_maps": ["Ascent", "Fracture", "Lotus"],
        "meta_by_map": existing,
    }
    print(f"\nScraped maps: {list(all_data.keys())}")
    sample = next(iter(all_data))
    for nm, st in list(all_data[sample].items())[:3]:
        print(f"  {sample} → {nm}: {st}")

    if dry_run:
        print("\n--dry-run: not writing.")
        return
    json.dump(out, open(META_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\nWritten to {META_PATH}. Restart the app to load fresh data.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", nargs="*", default=ACTIVE_MAPS)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    run(args.maps, args.dry_run)
