"""
MetaBot.GG scraper — the automated stats source behind data/vct_meta.json.

MetaBot serves server-rendered HTML tables (no JS wall), so a plain HTTP
request + BeautifulSoup is enough. Table columns (per map agents page):
Rank | Agent | Tier | Role | KDA | Matches | Win Rate | Pick Rate | View.

Used by the backend refresh endpoint (backend/meta_refresh.py) and the
tools/update_meta_from_metabot.py CLI.
"""
import json
import os
import re
import time
from datetime import date
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
META_PATH = os.path.join(BASE_DIR, "data", "vct_meta.json")

USER_AGENT = "Mozilla/5.0 (compatible; GydVLRCompBuilder/1.0)"
REQUEST_DELAY_SECONDS = 2.0  # be polite between map pages

# Fallbacks when no existing vct_meta.json provides them
DEFAULT_ACTIVE_MAPS = ["Ascent", "Breeze", "Fracture", "Haven", "Lotus", "Pearl", "Split"]
DEFAULT_THIN_MAPS = ["Ascent", "Fracture", "Lotus"]

PCT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)


def _agent_name_from_link(link) -> Optional[str]:
    """
    Agent name from a row's portrait link, or None if this isn't one.

    Only the portrait cell carries an <img>; "View Agent" buttons don't.
    Prefer the img alt over the href slug — KAY/O's href contains an
    unencoded slash that would truncate the slug to "KAY". Rows MetaBot
    itself renders broken (UUID href, no img, raw UUID as text) are dropped.
    """
    img = link.find("img")
    if img is None:
        return None
    name = (img.get("alt") or "").strip()
    if not name:
        match = re.search(r"/valorant/agent/([^/]+)/", link.get("href", ""))
        if not match:
            return None
        name = requests.utils.unquote(match.group(1))
    if UUID_RE.match(name):
        return None
    return name


def scrape_map(map_name: str) -> Dict[str, dict]:
    """One map's agent stats from MetaBot: {agent: {win_rate, pick_rate}}."""
    url = f"https://metabot.gg/en/valorant/map/{map_name}/agents"
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    result: Dict[str, dict] = {}
    for link in soup.select("a[href*='/valorant/agent/']"):
        row = link.find_parent("tr")
        if row is None:
            continue
        name = _agent_name_from_link(link)
        if name is None:
            continue
        if name in result:
            continue  # first table on the page is the combined "All" view
        pcts = PCT_RE.findall(row.get_text(" "))
        if len(pcts) >= 2:
            # Column order: Win Rate then Pick Rate
            result[name] = {
                "win_rate": float(pcts[0]),
                "pick_rate": float(pcts[1]),
            }
    return result


def _load_existing() -> dict:
    try:
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def refresh_meta(maps: Optional[list] = None, write: bool = True) -> dict:
    """
    Scrape the active pool and rewrite data/vct_meta.json (merging over any
    maps not rescraped, so out-of-rotation data survives as backup).
    Returns a summary: {maps: {name: agent_count}, errors: {name: msg}, ...}.
    """
    existing = _load_existing()
    active_maps = existing.get("active_maps") or DEFAULT_ACTIVE_MAPS
    thin_maps = existing.get("thin_maps") or DEFAULT_THIN_MAPS
    targets = maps or active_maps

    scraped: Dict[str, dict] = {}
    errors: Dict[str, str] = {}
    for i, map_name in enumerate(targets):
        try:
            data = scrape_map(map_name)
            if data:
                scraped[map_name] = data
            else:
                errors[map_name] = "no agent rows parsed (layout change?)"
        except requests.RequestException as exc:
            errors[map_name] = str(exc)
        if i < len(targets) - 1:
            time.sleep(REQUEST_DELAY_SECONDS)

    summary = {
        "maps": {m: len(d) for m, d in scraped.items()},
        "errors": errors,
        "written": False,
        "last_updated": existing.get("last_updated"),
    }
    if not scraped:
        return summary

    meta_by_map = existing.get("meta_by_map", {})
    meta_by_map.update(scraped)
    out = {
        "last_updated": date.today().isoformat(),
        "series": "MetaBot.GG · 2026 Ranked (Masters London pool)",
        "note": "Win/pick rates auto-scraped from MetaBot ranked data. "
                "Recently-rotated maps may show limited data.",
        "active_maps": active_maps,
        "thin_maps": thin_maps,
        "meta_by_map": meta_by_map,
    }
    if write:
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        summary["written"] = True
        summary["last_updated"] = out["last_updated"]
    return summary
