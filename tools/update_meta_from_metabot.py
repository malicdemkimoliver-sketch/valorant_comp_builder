"""
update_meta_from_metabot.py — refresh data/vct_meta.json from MetaBot.GG.

Thin CLI wrapper around app/services/meta_scraper.py (the same code the
backend's POST /api/meta/refresh endpoint runs), so there is exactly one
parser to maintain.

USAGE (from the repo root):
    python tools/update_meta_from_metabot.py              # all active maps
    python tools/update_meta_from_metabot.py --dry-run    # scrape, don't write
    python tools/update_meta_from_metabot.py --maps Haven Split
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.meta_scraper import refresh_meta  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    summary = refresh_meta(maps=args.maps, write=not args.dry_run)
    for map_name, count in summary["maps"].items():
        print(f"  {map_name}: {count} agents")
    for map_name, err in summary["errors"].items():
        print(f"  {map_name}: ERROR {err}")
    if summary["written"]:
        print(f"Written to data/vct_meta.json (last_updated={summary['last_updated']})")
        print("Tip: rerun tools/generate_presets.py, or use POST /api/meta/refresh "
              "which does both automatically.")
    elif args.dry_run:
        print("--dry-run: not writing.")
    else:
        print("Nothing scraped — file not written.")
