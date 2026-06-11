"""
update_meta_from_vstats.py — refresh data/vct_meta.json from vstats.gg
(Season 26 Act 3 ranked data, all agents per map)

vstats.gg renders its tables with JavaScript, so this drives a real headless
browser (Playwright). It reads the per-map agent table for each Masters London
map and writes data/vct_meta.json in the structure the app expects.

SETUP (one time):
    pip install playwright --break-system-packages
    python -m playwright install chromium

USAGE:
    cd C:\\Users\\kimma\\Documents\\valcompbuilder
    python tools\\update_meta_from_vstats.py               # all London maps
    python tools\\update_meta_from_vstats.py --dry-run     # preview only
    python tools\\update_meta_from_vstats.py --maps Haven Split
    python tools\\update_meta_from_vstats.py --debug       # dump page text if parsing fails

FALLBACK (if the site layout changes):
    1. Open vstats.gg, filter the agent table to a map
    2. Select the whole table, copy, paste into e.g. haven.txt
    3. python tools\\update_meta_from_vstats.py --from-paste haven.txt --map Haven
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

ACTIVE_MAPS = ["Ascent", "Breeze", "Fracture", "Haven", "Lotus", "Pearl", "Split"]
THIN_MAPS = ["Ascent", "Fracture", "Lotus"]

AGENT_NAMES = {
    "Jett", "Raze", "Neon", "Reyna", "Phoenix", "Yoru", "Iso", "Waylay",
    "Omen", "Brimstone", "Viper", "Astra", "Clove", "Harbor", "Miks",
    "Sova", "Fade", "Breach", "Skye", "Gekko", "KAY/O", "Tejo",
    "Killjoy", "Cypher", "Sage", "Deadlock", "Chamber", "Vyse", "Veto",
}
NAME_FIXES = {"KAYO": "KAY/O", "Kayo": "KAY/O", "KAY/0": "KAY/O"}


def _norm(raw):
    raw = raw.strip()
    raw = NAME_FIXES.get(raw, raw)
    for canon in AGENT_NAMES:
        if raw.lower() == canon.lower():
            return canon
    return None


def scrape_map(page, map_name, debug=False):
    url = f"https://www.vstats.gg/VALORANT?map={map_name}"
    page.goto(url, wait_until="networkidle", timeout=60_000)
    time.sleep(3.0)

    result = {}
    rows = page.query_selector_all("table tr, [role='row'], .agent-row, li")
    for row in rows:
        try:
            txt = row.inner_text()
        except Exception:
            continue
        if not txt or "%" not in txt:
            continue
        name = None
        for token in re.split(r"[\t\n|]+|\s{2,}", txt):
            name = _norm(re.sub(r"[\d.%,()]", "", token).strip())
            if name:
                break
        if not name or name in result:
            continue
        pcts = re.findall(r"(\d+(?:[.,]\d+)?)\s*%", txt)
        if len(pcts) >= 2:
            pr = float(pcts[0].replace(",", "."))
            wr = float(pcts[1].replace(",", "."))
            result[name] = {"pick_rate": pr, "win_rate": wr}

    if debug and not result:
        dump = os.path.join(BASE_DIR, f"vstats_debug_{map_name}.txt")
        with open(dump, "w", encoding="utf-8") as f:
            f.write(page.inner_text("body"))
        print(f"    [debug] no rows parsed; page text dumped to {dump}")
    return result


def run_scrape(maps, dry_run=False, debug=False):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Run:")
        print("    pip install playwright --break-system-packages")
        print("    python -m playwright install chromium")
        sys.exit(1)

    all_data = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for i, m in enumerate(maps):
            print(f"[{i+1}/{len(maps)}] {m}...", end=" ", flush=True)
            try:
                data = scrape_map(page, m, debug=debug)
                if data:
                    all_data[m] = data
                    flag = "  [THIN/limited]" if m in THIN_MAPS else ""
                    print(f"OK {len(data)} agents{flag}")
                else:
                    print("no rows (try --debug, or --from-paste fallback)")
            except Exception as e:
                print(f"ERROR {e}")
            time.sleep(3.0)
        browser.close()

    if not all_data:
        print("\nNothing scraped. Use --debug or --from-paste fallback.")
        sys.exit(1)
    _write(all_data, dry_run)


def run_paste(paste_file, map_name, dry_run=False):
    text = open(paste_file, encoding="utf-8").read()
    data = {}
    for line in text.splitlines():
        if "%" not in line:
            continue
        name = None
        for token in re.split(r"[\t]+|\s{2,}", line):
            name = _norm(re.sub(r"[\d.%,()]", "", token).strip())
            if name:
                break
        if not name:
            continue
        pcts = [float(x.replace(",", ".")) for x in re.findall(r"(\d+(?:[.,]\d+)?)\s*%", line)]
        if len(pcts) >= 2:
            data[name] = {"pick_rate": pcts[0], "win_rate": pcts[1]}
    if not data:
        print("Could not parse any rows.")
        sys.exit(1)
    print(f"Parsed {len(data)} agents for {map_name}")
    _write({map_name: data}, dry_run)


def _write(scraped, dry_run):
    existing = {}
    if os.path.exists(META_PATH):
        try:
            existing = json.load(open(META_PATH, encoding="utf-8")).get("meta_by_map", {})
        except Exception:
            pass
    existing.update(scraped)

    out = {
        "last_updated": date.today().isoformat(),
        "series": "vstats.gg · Season 26 Act 3 (Masters London pool)",
        "note": "Ranked data from vstats.gg. Recently-rotated maps may be unreliable.",
        "active_maps": ACTIVE_MAPS,
        "thin_maps": THIN_MAPS,
        "meta_by_map": existing,
    }
    print(f"\nScraped: {[(m, len(d)) for m, d in scraped.items()]}")
    sample = next(iter(scraped))
    for nm, st in list(scraped[sample].items())[:3]:
        print(f"  {sample} -> {nm}: {st}")
    if dry_run:
        print("\n--dry-run: not writing.")
        return
    json.dump(out, open(META_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\nWritten to {META_PATH}. Restart the app.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", nargs="*", default=ACTIVE_MAPS)
    ap.add_argument("--from-paste")
    ap.add_argument("--map")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()
    if args.from_paste:
        if not args.map:
            print("--from-paste requires --map <MapName>")
            sys.exit(1)
        run_paste(args.from_paste, args.map, args.dry_run)
    else:
        run_scrape(args.maps, args.dry_run, args.debug)
