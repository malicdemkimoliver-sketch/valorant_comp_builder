"""
Catalog — merges the canonical valorant-api.com roster with the curated
overlay data that powers scoring and suggestions (data/agents.json,
data/maps.json, data/vct_meta.json).

valorant-api supplies: roster, roles, portraits, abilities, map art.
Curated files supply: strengths/weaknesses, good_maps, synergy_tags, utility.
Agents the API knows but the curated data doesn't (e.g. brand-new releases)
come through with curated=False and empty overlay fields — visible in the UI,
rated purely by their pick/win-rate meta data until curated.
"""
import json
import os
from typing import List, Optional

from app.services import meta_service
from backend import valorant_api

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

OVERLAY_FIELDS = ("strengths", "weaknesses", "good_maps", "synergy_tags", "utility")


def _load_json(filename: str) -> list:
    try:
        with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_agents() -> List[dict]:
    curated = {a["name"]: a for a in _load_json("agents.json")}
    api_agents = valorant_api.get_agents()

    if api_agents is None:
        # Fully offline with no cache: serve curated data alone.
        return [
            {
                "uuid": None,
                "name": c["name"],
                "description": "",
                "role": c.get("role", ""),
                "display_icon": None,
                "full_portrait": None,
                "background_colors": [],
                "abilities": [],
                "icon": c.get("icon", ""),
                **{f: c.get(f, []) for f in OVERLAY_FIELDS},
                "curated": True,
            }
            for c in curated.values()
        ]

    merged = []
    for a in sorted(api_agents, key=lambda x: x["name"]):
        c = curated.get(a["name"], {})
        merged.append(
            {
                **a,
                "icon": c.get("icon", ""),
                **{f: c.get(f, []) for f in OVERLAY_FIELDS},
                "curated": a["name"] in curated,
            }
        )
    return merged


def get_agent(name: str) -> Optional[dict]:
    target = name.strip().lower()
    for agent in get_agents():
        if agent["name"].lower() == target:
            return agent
    return None


def get_maps() -> List[dict]:
    curated = _load_json("maps.json")
    api_maps = {m["name"]: m for m in (valorant_api.get_maps() or [])}
    meta = meta_service.load_meta_data()
    active = set(meta.get("active_maps", []))
    maps_with_data = set(meta_service.get_all_maps())

    out = []
    for m in curated:
        api = api_maps.get(m["name"], {})
        out.append(
            {
                **m,
                "uuid": api.get("uuid"),
                "splash": api.get("splash"),
                "list_view_icon": api.get("list_view_icon"),
                "sites": api.get("sites"),
                "in_active_pool": m["name"] in active,
                "has_meta_data": m["name"] in maps_with_data,
            }
        )
    return out


def get_map(name: str) -> Optional[dict]:
    target = name.strip().lower()
    for m in get_maps():
        if m["name"].lower() == target:
            return m
    return None
