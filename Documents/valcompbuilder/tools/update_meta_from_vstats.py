"""
update_meta_from_vstats.py — refresh data/vct_meta.json from vstats.gg

vstats.gg renders its tables with JavaScript, so this tool drives a real
headless browser (Playwright) on YOUR machine, reads the agent table for
each map, and writes data/vct_meta.json in the structure the app expects:

    {
      "last_updated": "2026-06-10",
      "series": "vstats.gg · Season 26 Act 3",
      "meta_by_map": {
        "Ascent": { "Jett": {"pick_rate": 12.3, "win_rate": 51.2}, ... },
        ...
      }
    }

SETUP (one time):
    pip install playwright --break-system-packages
    python -m playwright install chromium

USAGE:
    cd C:\\Users\\kimma\\Documents\\valcompbuilder
    python tools\\update_meta_from_vstats.py                # all maps
    python tools\\update_meta_from_vstats.py --maps Ascent Bind
    python tools\\update_meta_from_vstats.py --dry-run      # preview only

FALLBACK (if scraping breaks after a site redesign):
    1. Open vstats.gg in your browser, filter the agent table to a map
    2. Select the whole table, copy, paste into a text file e.g. ascent.txt
    3. python tools\\update_meta_from_vstats.py --from-paste ascent.txt --map Ascent

NOTE: be a good citizen — this visits one page per map with delays between
requests. Don't run it in a loop; once per patch/act is plenty.
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

DEFAULT_MAPS = ["Ascent", "Bind", "Breeze", "Fracture", "Haven",
                "Icebox", "Lotus", "Pearl", "Split", "Abyss", "Sunset", "Corrode"]

AGENT_NAMES = {
    "Jett", "Raze", "Neon", "Reyna", "Phoenix", "Yoru", "Iso", "Waylay",
    "Omen", "Brimstone", "Viper", "Astra", "Clove", "Harbor",
    "Sova", "Fade", "Breach", "Skye", "Gekko", "KAY/O", "Tejo",
    "Killjoy", "Cypher", "Sage", "Deadlock", "Chamber", "Vyse", "Veto",
}
# vstats may render KAY/O as KAYO or Kay/o
NAME_FIXES = {"KAYO": "KAY/O", "Kayo": "KAY/O", "Kay/o": "KAY/O", "KAY/o": "KAY/O"}


def _norm_name(raw: str):
    raw = raw.strip()
    raw = NAME_FIXES.get(raw, raw)
    for canonical in AGENT_NAMES:
        if raw.lower() == canonical.lower():
            return canonical
    return None


def _pct(text: str):
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", text)
    return float(m.group(1).replace(",", ".")) if m else None


# ── Strategy 1: Playwright scrape ────────────────────────────────────────────
def scrape_map(page, map_name: str) -> dict:
    """Scrape the agent table for one map. Returns {agent: {pick_rate, win_rate}}."""
    url = f"https://www.vstats.gg/agents?map={map_name}"
    page.goto(url, wait_until="networkidle", timeout=60_000)
    time.sleep(2.0)  # let late XHRs settle

    # Read every table row; figure out columns from the header
    result = {}
    rows = page.query_selector_all("table tr")
    if not rows:
        # some layouts use role=row divs
        rows = page.query_selector_all('[role="row"]')

    header_cells, wr_idx, pr_idx, nm_idx = [], None, None, 0
    for row in rows:
        cells = row.query_selector_all("td, th, [role='cell'], [role='columnheader']")
        texts = [c.inner_text().strip() for c in cells]
        if not texts:
            continue

        # Header row: locate column indices (prefer non-mirror win rate)
        lower = [t.lower() for t in texts]
        if any("win" in t and "rate" in t for t in lower) and wr_idx is None:
            for i, t in enumerate(lower):
                if "non-mirror" in t and "win" in t:
                    wr_idx = i
            if wr_idx is None:
                for i, t in enumerate(lower):
                    if "win" in t and "rate" in t:
                        wr_idx = i
                        break
            for i, t in enumerate(lower):
                if "pick" in t and "rate" in t:
                    pr_idx = i
                    break
            continue

        # Data row
        name = None
        for t in texts[:3]:
            name = _norm_name(re.sub(r"[\d.%,]", "", t).strip())
            if name:
                break
        if not name:
            continue

        wr = _pct(texts[wr_idx]) if wr_idx is not None and wr_idx < len(texts) else None
        pr = _pct(texts[pr_idx]) if pr_idx is not None and pr_idx < len(texts) else None
        if wr is None or pr is None:
            # fall back: first two percentages in the row
            pcts = [_pct(t) for t in texts if _pct(t) is not None]
            if len(pcts) >= 2:
                pr = pr if pr is not None else pcts[0]
                wr = wr if wr is not None else pcts[1]
        if wr is not None and pr is not None:
            result[name] = {"pick_rate": pr, "win_rate": wr}

    return result


def run_scrape(maps, dry_run=False):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("✗ Playwright not installed. Run:")
        print("    pip install playwright --break-system-packages")
        print("    python -m playwright install chromium")
        sys.exit(1)

    all_data = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for i, m in enumerate(maps):
            print(f"[{i+1}/{len(maps)}] Scraping {m}...", end=" ", flush=True)
            try:
                data = scrape_map(page, m)
                if data:
                    all_data[m] = data
                    print(f"✓ {len(data)} agents")
                else:
                    print("✗ no rows found (map may be out of rotation, or layout changed — use --from-paste)")
            except Exception as e:
                print(f"✗ {e}")
            time.sleep(3.0)  # polite delay between pages
        browser.close()

    if not all_data:
        print("\nNothing scraped. Try the --from-paste fallback (see file header).")
        sys.exit(1)
    _write(all_data, dry_run)


# ── Strategy 2: paste-in fallback ────────────────────────────────────────────
def run_paste(paste_file: str, map_name: str, dry_run=False):
    """Parse a copy-pasted table (tab/space separated) for one map."""
    with open(paste_file, "r", encoding="utf-8") as f:
        text = f.read()

    data = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        name = None
        for token in re.split(r"[\t]+|\s{2,}", line):
            name = _norm_name(re.sub(r"[\d.%,]", "", token).strip())
            if name:
                break
        if not name:
            continue
        pcts = [float(x.replace(",", ".")) for x in re.findall(r"(\d+(?:[.,]\d+)?)\s*%", line)]
        if len(pcts) >= 2:
            # vstats column order: pick rate usually before win rate
            data[name] = {"pick_rate": pcts[0], "win_rate": pcts[1]}

    if not data:
        print("✗ Could not parse any agent rows from the paste file.")
        sys.exit(1)
    print(f"✓ Parsed {len(data)} agents for {map_name}")

    # merge into existing file
    existing = {}
    if os.path.exists(META_PATH):
        try:
            with open(META_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f).get("meta_by_map", {})
        except Exception:
            pass
    existing[map_name] = data
    _write(existing, dry_run)


def _write(meta_by_map: dict, dry_run: bool):
    out = {
        "last_updated": date.today().isoformat(),
        "series": "vstats.gg · ranked data",
        "note": "Win rates prefer non-mirror WR where the site provides it.",
        "meta_by_map": meta_by_map,
    }
    print(f"\nMaps: {list(meta_by_map.keys())}")
    sample_map = next(iter(meta_by_map))
    sample = list(meta_by_map[sample_map].items())[:3]
    for name, st in sample:
        print(f"  {sample_map} → {name}: {st}")

    if dry_run:
        print("\n--dry-run: not writing file.")
        return
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Written to {META_PATH}")
    print("Restart the app to load fresh meta data.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", nargs="*", default=DEFAULT_MAPS)
    ap.add_argument("--from-paste", help="Path to a pasted-table text file")
    ap.add_argument("--map", help="Map name for --from-paste")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.from_paste:
        if not args.map:
            print("✗ --from-paste requires --map <MapName>")
            sys.exit(1)
        run_paste(args.from_paste, args.map, args.dry_run)
    else:
        run_scrape(args.maps, args.dry_run)
